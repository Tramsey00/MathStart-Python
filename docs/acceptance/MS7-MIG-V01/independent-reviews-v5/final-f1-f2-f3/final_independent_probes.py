import os,json,threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import sqlalchemy as sa
from backend.tests.test_postgres import PostgreSQLTests
from backend.models.baseline import metadata
from backend.infrastructure.collector import delete_collected
from backend.infrastructure.locks import OrderedLocks
from backend.infrastructure.uow import UnitOfWork
from backend.tests.test_remediation import RemediationTests

results=[]
PostgreSQLTests.setUpClass()
try:
 for leader in (1,2):
  with PostgreSQLTests().database() as engine:
   RemediationTests().crossed_catalog(engine)
   barrier=threading.Barrier(2);leader_locked=threading.Event();follower_attempt=threading.Event()
   states=[];tokens={};guard=threading.Lock();changed=[]
   @sa.event.listens_for(engine,'before_cursor_execute')
   def before(connection,cursor,statement,parameters,context,executemany):
    if 'FROM content_grade' in statement and 'FOR UPDATE' in statement and not connection.info.get('audit_started'):
     connection.info['audit_started']=True
     identity=connection.info['audit_identity'];barrier.wait(timeout=10)
     if identity!=leader:
      assert leader_locked.wait(10);follower_attempt.set()
   @sa.event.listens_for(engine,'after_cursor_execute')
   def after(connection,cursor,statement,parameters,context,executemany):
    if 'FROM content_grade' in statement and 'FOR UPDATE' in statement and connection.info.get('audit_identity')==leader and not leader_locked.is_set():
     # A non-key concurrent update must survive collector SET_NULL.
     with engine.begin() as other: other.execute(sa.text("UPDATE content_contentpage SET title='Concurrent retained title' WHERE id=1"))
     changed.append(True);leader_locked.set();assert follower_attempt.wait(10)
   @sa.event.listens_for(engine,'handle_error')
   def capture(context):
    with guard:states.append(getattr(context.original_exception,'sqlstate',None))
   class RecordingLocks(OrderedLocks):
    def __init__(self,session):super().__init__(session);self.seen=[]
    def _advance(self,token):super()._advance(token);self.seen.append(token)
   def remove(identity):
    try:
     with UnitOfWork(engine) as u:
      u.session.connection().info['audit_identity']=identity
      locks=RecordingLocks(u.session)
      delete_collected(u.session,'content_grade',[identity],locks=locks)
      tokens[identity]=locks.seen;u.commit()
     return 'COMMIT'
    except Exception as error:return type(error).__name__
   with ThreadPoolExecutor(2) as pool:
    outcomes=list(pool.map(remove,(leader,3-leader)))
   with engine.connect() as c:
    pages=[tuple(row) for row in c.execute(sa.text('SELECT id,grade_id,subject_id,section_id FROM content_contentpage ORDER BY id'))]
    title=c.scalar(sa.text('SELECT title FROM content_contentpage WHERE id=1'))
    counts={name:c.scalar(sa.select(sa.func.count()).select_from(metadata.tables[name])) for name in ['content_grade','content_subject','content_section','content_lessonpublication']}
   assert outcomes==['COMMIT','COMMIT'] and states==[]
   assert pages==[(1,None,None,None),(2,None,None,None)]
   assert title=='Concurrent retained title' and changed
   assert counts=={'content_grade':0,'content_subject':0,'content_section':0,'content_lessonpublication':2}
   assert all(sequence==sorted(sequence) for sequence in tokens.values())
   results.append({'forced_first_locker':leader,'outcomes':outcomes,'sqlstates':states,'page_foreign_keys':pages,'concurrent_non_key_update_preserved':True,'counts':counts,'lock_tokens':tokens})
finally:PostgreSQLTests.tearDownClass()
Path('independent-f2-two-orders.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
