"""Synthetic R02 protocol model and adversarial traces, never target runtime.

No application service, thread, database, ticket signer or filesystem activation
is implemented here. Literal expected outcomes exercise ordering and rejected
effects; table/schema coverage prevents a prose-only amendment. V03/V04 must
replace these claims with real populated migration, transaction and race proof.
"""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'specs/migration/r02-v1'

def load(name):
    return json.loads((P / name).read_text(encoding='utf-8'))

def validator(name):
    return Draft202012Validator({'$defs': load('delivery-v1.schema.json')['$defs'],
                                '$ref': '#/$defs/' + name}, format_checker=FormatChecker())

class Denied(Exception):
    pass

class PublicationModel:
    """Abstract atomic authority transactions; explicit simulated clock/ACK loss."""
    def __init__(self):
        self.generation = 0
        self.pending = None
        self.active = ('initial', 'old', 'a' * 64, 0)
        self.db = ('old', 'a' * 64)
        self.journals = {}
        self.keys = {}
        self.domain_writes = 0
        self.effects = []

    def claim(self, op, owner, now=0, plan='b' * 64, expected='old', key=None):
        key = key or op
        if key in self.keys:
            op = self.keys[key]
        if op in self.journals:
            if self.journals[op]['plan'] != plan:
                raise Denied('PLAN_CONFLICT')
            return self.journals[op]['stage']  # read-only operation lookup
        if self.pending:
            raise Denied('BUSY')
        if self.active[1:3] != self.db or self.active[1] != expected:
            raise Denied('EXPECTED_CONFLICT')
        self.generation += 1
        self.pending = op
        self.keys[key] = op
        self.journals[op] = dict(owner=owner, gen=self.generation, lease=now+10,
                                 stage='VALIDATED', plan=plan, previous=self.active,
                                 next=(op, 'next-'+op, 'b'*64), committed=False,
                                 activation='NOT_STARTED')
        return (op, owner, self.generation)

    def check(self, token, now):
        op, owner, gen = token
        j = self.journals[op]
        if self.pending != op or (owner, gen) != (j['owner'], j['gen']) or now >= j['lease']:
            raise Denied('FENCED')
        return j

    def renew(self, token, now):
        j = self.check(token, now)
        j['lease'] = now+10
        return 'RENEWED'

    def takeover(self, op, observed, owner, now):
        j = self.journals[op]
        if self.pending != op:
            raise Denied('TERMINAL')
        if observed != j['gen']:
            raise Denied('CLAIM_CONFLICT')
        if now < j['lease']:
            raise Denied('OWNER_BUSY')
        self.generation += 1
        j.update(owner=owner, gen=self.generation, lease=now+10)
        if j['committed']:
            j['stage'] = 'RECOVERY_REQUIRED'  # reconcile before any new effect
        return (op, owner, self.generation)

    def stage(self, token, now=1, valid_hashes=True):
        j = self.check(token, now)
        if not valid_hashes:
            raise Denied('HASH_CONFLICT')
        if j['stage'] == 'STAGED':
            return 'STAGED'
        if j['stage'] != 'VALIDATED':
            raise Denied('PHASE')
        j['stage'] = 'STAGED'
        return 'STAGED'

    def commit(self, token, now=2, expected_source=True):
        j = self.check(token, now)
        if j['committed']:
            return 'DB_COMMITTED'
        if j['stage'] != 'STAGED' or not expected_source or self.active != j['previous']:
            raise Denied('EXPECTED_CONFLICT')
        self.db = j['next'][1:]
        self.domain_writes += 1
        j.update(stage='DB_COMMITTED', committed=True)
        return 'DB_COMMITTED'

    def intent(self, token, now=3):
        j = self.check(token, now)
        if j['stage'] == 'ACTIVATING':
            return 'ACTIVATING'
        if j['stage'] != 'DB_COMMITTED':
            raise Denied('PHASE')
        j.update(stage='ACTIVATING', activation='UNKNOWN')
        return 'ACTIVATING'

    def activate(self, token, now=4):
        j = self.check(token, now)
        if self.active[:3] == j['next']:
            return 'ALREADY_ACTIVATED'
        if j['stage'] != 'ACTIVATING':
            raise Denied('PHASE')
        if self.active != j['previous']:
            raise Denied('POINTER_CONFLICT')
        self.active = j['next']+(j['gen'],)
        j.update(stage='ACTIVATED', activation='APPLIED')
        self.effects.append(('activate', self.active))
        return 'ACTIVATED'

    def uncertain(self, token, now=5):
        j = self.check(token, now)
        if not j['committed']:
            raise Denied('PHASE')
        j.update(stage='RECOVERY_REQUIRED', activation='UNKNOWN')
        return 'RECOVERY_REQUIRED'

    def reconcile(self, token, now=6):
        j = self.check(token, now)
        if not j['committed']:
            raise Denied('PHASE')
        if self.active[:3] == j['next']:
            j.update(stage='ACTIVATED', activation='APPLIED')
            return 'APPLIED'
        if self.active == j['previous']:
            j.update(stage='DB_COMMITTED', activation='NOT_APPLIED')
            return 'NOT_APPLIED'
        raise Denied('POINTER_CONFLICT')

    def complete(self, token, now=7, probes=True):
        j = self.check(token, now)
        if j['stage'] != 'ACTIVATED' or self.active[:3] != j['next'] or self.active[1:3] != self.db:
            raise Denied('PHASE')
        if not probes:
            j['stage'] = 'RECOVERY_REQUIRED'
            return 'RECOVERY_REQUIRED'
        j['stage'] = 'COMPLETE'
        self.pending = None
        return 'COMPLETE'

    def abort(self, token, now=3):
        j = self.check(token, now)
        if j['committed']:
            raise Denied('COMMITTED')
        j['stage'] = 'FAILED_PRECOMMIT'
        self.pending = None
        return 'FAILED_PRECOMMIT'

    def cleanup(self, token, now=5):
        self.check(token, now)
        raise Denied('REFERENCED')  # pending/active roots never disposable

class BridgeModel:
    """Abstract lifecycle state. All proof values below are synthetic booleans."""
    def __init__(self):
        self.owner = 'alice'
        self.scope = 'bootstrap:original'
        self.receipt = {'scope': self.scope, 'owner': self.owner, 'key': 'key1',
                        'digest': 'immutable-body', 'status': 201, 'response': 'original-safe-bytes'}
        self.receipt_hash = hashlib.sha256(json.dumps(self.receipt, sort_keys=True).encode()).hexdigest()
        self.state = 'ACTIVE'
        self.session = 'session-A'
        self.lineage = 'lineage-A'
        self.epoch = 1
        self.ticket_version = 1
        self.ticket_revoked = False
        self.ticket_expiry = 90
        self.replay_until = 100
        self.transfer = True
        self.sessions_minted = 0
        self.owner_active = True
        self.cutover_checkpoint = None

    def transition(self, event, checkpoint='cutover-1', drained=True, verified=True):
        if event == 'cutover':
            if self.cutover_checkpoint == checkpoint:
                return self.state
            if self.cutover_checkpoint is not None or not drained or not verified:
                raise Denied('STOP_WRITES')
            self.cutover_checkpoint = checkpoint
        if self.state in ['REVOKED', 'EXPIRED']:
            return self.state
        if event in ['logout', 'account_switch', 'security_revoke']:
            self.state = 'REVOKED'
            self.ticket_revoked = True
            self.transfer = False
        elif event in ['session_expiry', 'cutover']:
            if self.state == 'DETACHED':
                return self.state
            self.state = 'DETACHED'
        elif event == 'replay_window_expiry':
            self.state = 'EXPIRED'
            self.ticket_revoked = True
            self.transfer = False
        else:
            raise Denied('EVENT')
        self.epoch += 1
        self.session = None
        return self.state

    def repeat_login(self, actor):
        if actor != self.owner or self.state != 'ACTIVE':
            raise Denied('STATE_CONFLICT')
        self.epoch += 1
        self.ticket_version += 1
        self.session = 'rotated-'+str(self.epoch)
        return self.session

    def replay(self, proof, actor=None, password=True, original=True, ticket=True,
               ticket_version=1, epoch=1, session='session-A', now=20,
               key='key1', digest='immutable-body', rebind=False):
        if self.state in ['REVOKED', 'EXPIRED'] or now >= self.replay_until or not self.owner_active:
            raise Denied('STATE_CONFLICT')
        if actor is not None and actor != self.owner:
            raise Denied('STATE_CONFLICT')
        if epoch != self.epoch:
            raise Denied('STATE_CONFLICT')
        if proof == 'S':
            good = actor == self.owner and self.state == 'ACTIVE' and session == self.session
        elif proof == 'B':
            good = original and (actor == self.owner or (actor is None and password))
        elif proof == 'T':
            good = (ticket and original and not self.ticket_revoked and now < self.ticket_expiry
                    and ticket_version == self.ticket_version and (actor == self.owner or (actor is None and password)))
        elif proof == 'F':
            good = self.transfer and actor == self.owner
        else:
            good = False
        if not good:
            raise Denied('STATE_CONFLICT')
        if key != self.receipt['key'] or digest != self.receipt['digest']:
            raise Denied('IDEMPOTENCY_CONFLICT')
        if rebind or actor is None:
            self.epoch += 1
            self.ticket_version += 1
            self.state = 'ACTIVE'
            self.session = 'recovered-'+str(self.epoch)
            self.sessions_minted += 1
        return (201, 'original-safe-bytes')

class PublicationProtocolTests(unittest.TestCase):
    def prepared(self):
        m = PublicationModel(); token = m.claim('one', 'worker-A')
        m.stage(token); m.commit(token)
        return m, token

    def assert_rejected_without_effect(self, m, command, code='FENCED'):
        before = copy.deepcopy(m.__dict__)
        with self.assertRaisesRegex(Denied, code): command()
        self.assertEqual(m.__dict__, before)

    def test_claim_stage_commit_activation_complete_and_repeats(self):
        m = PublicationModel(); t = m.claim('one', 'worker-A')
        self.assertEqual(m.claim('one', 'worker-X'), 'VALIDATED')
        for name, result in [('stage','STAGED'),('commit','DB_COMMITTED'),('intent','ACTIVATING')]:
            self.assertEqual(getattr(m,name)(t),result); self.assertEqual(getattr(m,name)(t),result)
        self.assertEqual(m.activate(t), 'ACTIVATED'); self.assertEqual(m.activate(t), 'ALREADY_ACTIVATED')
        self.assertEqual(m.complete(t),'COMPLETE'); self.assertIsNone(m.pending)
        newer=m.claim('two','worker-B',now=8,expected='next-one')
        self.assertEqual(newer[2],2)
        self.assertEqual(m.claim('one','worker-X'),'COMPLETE')
        self.assertEqual(m.active[1],'next-one'); self.assertEqual(m.domain_writes,1)

    def test_pending_gate_survives_crash_expiry_and_db_commit(self):
        m,t=self.prepared()
        self.assert_rejected_without_effect(m,lambda:m.claim('two','worker-B',now=100), 'BUSY')
        self.assert_rejected_without_effect(m,lambda:m.abort(t), 'COMMITTED')
        self.assertEqual(m.active[1],'old'); self.assertEqual(m.db[0],'next-one')
        self.assertEqual(m.pending,'one'); self.assertEqual(m.domain_writes,1)

    def test_same_key_new_uuid_resolves_original_operation_without_new_write(self):
        m,t=self.prepared();m.intent(t);m.activate(t);m.complete(t)
        before=copy.deepcopy(m.__dict__)
        self.assertEqual(m.claim('different-uuid','worker-B',key='one'),'COMPLETE')
        self.assertEqual(m.__dict__,before)
        self.assert_rejected_without_effect(m,lambda:m.claim('different-uuid','worker-B',key='one',plan='changed'),'PLAN_CONFLICT')

    def test_competing_recovery_workers_both_orders_one_winner(self):
        for first,second in [('worker-B','worker-C'),('worker-C','worker-B')]:
            m,old=self.prepared(); new=m.takeover('one',1,first,10)
            self.assertEqual(new,('one',first,2))
            self.assert_rejected_without_effect(m,lambda:m.takeover('one',1,second,10),'CLAIM_CONFLICT')
            self.assert_rejected_without_effect(m,lambda:m.takeover('one',2,second,11),'OWNER_BUSY')
            self.assertEqual(m.reconcile(new,11),'NOT_APPLIED')
            m.intent(new,12);m.activate(new,13);m.complete(new,14)
            self.assertEqual(m.domain_writes,1);self.assertEqual(len(m.effects),1)

    def test_all_stale_owner_writes_are_fenced_even_with_returning_worker_id(self):
        m,old=self.prepared(); new=m.takeover('one',1,'worker-A',10)
        self.assertEqual(new[2],2)
        for name in ['renew','stage','commit','intent','activate','uncertain','reconcile','complete','abort','cleanup']:
            with self.subTest(command=name):
                self.assert_rejected_without_effect(m,lambda:getattr(m,name)(old,11))
        self.assertEqual(m.pending,'one');self.assertEqual(m.active[1],'old')

    def test_expired_current_owner_cannot_renew_or_activate(self):
        m,t=self.prepared();m.intent(t)
        for name in ['renew','activate','commit','complete']:
            self.assert_rejected_without_effect(m,lambda:getattr(m,name)(t,10))

    def test_activation_commit_before_takeover_reconciles_old_generation_history(self):
        m,t=self.prepared();m.intent(t);m.activate(t);m.uncertain(t)
        newer=m.takeover('one',1,'worker-B',10)
        self.assertEqual(m.active[3],1)
        self.assertEqual(m.reconcile(newer,11),'APPLIED')
        self.assertEqual(m.reconcile(newer,12),'APPLIED')
        m.complete(newer,13)
        self.assertEqual(m.domain_writes,1);self.assertEqual(len(m.effects),1)

    def test_takeover_before_delayed_activation_rejects_stale_effect(self):
        m,t=self.prepared();m.intent(t)
        newer=m.takeover('one',1,'worker-B',10)
        self.assert_rejected_without_effect(m,lambda:m.activate(t,11))
        self.assert_rejected_without_effect(m,lambda:m.activate(newer,11),'PHASE')
        self.assertEqual(m.reconcile(newer,11),'NOT_APPLIED')
        m.intent(newer,12);m.activate(newer,13);m.complete(newer,14)
        self.assertEqual(m.active[3],2)

    def test_unknown_activation_both_failure_windows_no_speculative_retry(self):
        for committed in [False,True]:
            m,t=self.prepared();m.intent(t)
            if committed:m.activate(t)
            m.uncertain(t)
            self.assert_rejected_without_effect(m,lambda:m.claim('two','worker-B'),'BUSY')
            self.assertEqual(m.reconcile(t), 'APPLIED' if committed else 'NOT_APPLIED')
            if not committed:m.intent(t,6);m.activate(t,7)
            m.complete(t,8)
            self.assertEqual(m.domain_writes,1);self.assertEqual(len(m.effects),1)

    def test_pointer_digest_or_operation_mismatch_never_reconciles_success(self):
        for descriptor in [('foreign','next-one','b'*64,1),('one','next-one','c'*64,1),('one','wrong','b'*64,1)]:
            m,t=self.prepared();m.intent(t);m.uncertain(t);m.active=descriptor
            self.assert_rejected_without_effect(m,lambda:m.reconcile(t),'POINTER_CONFLICT')
            self.assertEqual(m.pending,'one')

    def test_precommit_abort_terminal_and_hash_source_guards(self):
        m=PublicationModel();t=m.claim('one','worker-A')
        self.assert_rejected_without_effect(m,lambda:m.stage(t,valid_hashes=False),'HASH_CONFLICT')
        m.stage(t)
        self.assert_rejected_without_effect(m,lambda:m.commit(t,expected_source=False),'EXPECTED_CONFLICT')
        m.abort(t);self.assertEqual(m.claim('one','worker-A'),'FAILED_PRECOMMIT')
        self.assertEqual(m.domain_writes,0);self.assertIsNone(m.pending)
        self.assert_rejected_without_effect(m,lambda:m.claim('one','worker-A',plan='changed'),'PLAN_CONFLICT')
        self.assertEqual(m.claim('two','worker-B')[2],2)

    def test_health_failure_holds_slot_and_stale_probe_cannot_complete(self):
        m,t=self.prepared();m.intent(t);m.activate(t)
        self.assertEqual(m.complete(t,probes=False),'RECOVERY_REQUIRED')
        newer=m.takeover('one',1,'worker-B',10)
        self.assert_rejected_without_effect(m,lambda:m.complete(t,11))
        m.reconcile(newer,11);m.complete(newer,12)
        self.assertEqual(m.active[1:3],m.db)

    def test_machine_table_covers_every_failure_and_no_new_runtime_mapping(self):
        table=load('publication-protocol-v1.json')
        self.assertEqual({r['action'] for r in table['transitions']}, {'claim_new','stage','fail_precommit','commit','intent','activate','uncertain','reconcile_previous','reconcile_next','complete','takeover'})
        self.assertEqual([r['action'] for r in table['transitions'] if r['domain_write']=='ONCE'],['commit'])
        storage=load('protocol-storage-mapping-v1.json')
        self.assertEqual({r['record'] for r in storage['records']},{'PublicationGate','PublicationJournal','ActiveReleaseDescriptor','ReceiptBridge','StagedRelease'})
        self.assertEqual(table['evidence'],'MODEL_SYNTHETIC_ONLY')

    def test_schema_journal_and_observable_reject_impossible_commit_and_secret_owner(self):
        journal={'operation_id':'00000000-0000-4000-8000-000000000001','operation':'publish','stage':'ACTIVATING',
                 'previous_release':'old','next_release':'next-one','manifest_digest':'b'*64,'plan_digest':'c'*64,'key_digest':'d'*64,
                 'affected_paths':['/example/'],'updated_at':'2026-10-09T00:00:00Z','failure_code':None,'resume_cursor':'activate',
                 'owner_id':'00000000-0000-4000-8000-000000000002','fence_generation':2,'lease_until':'2026-10-09T00:01:00Z',
                 'db_committed':True,'activation_status':'UNKNOWN'}
        validator('PublicationJournal').validate(journal)
        for field,value in [('db_committed',False),('fence_generation',0),('fence_generation',True),('activation_status','APPLIED')]:
            with self.assertRaises(ValidationError):validator('PublicationJournal').validate({**journal,field:value})
        pending=next(s['pending'] for s in load('synthetic-review-exchanges-v1.json')['publication_states'] if s['pending'] and s['pending']['stage']=='ACTIVATING')
        validator('PendingPublicationState').validate(pending)
        for field,value in [('db_committed',False),('owner_id','private'),('ownership','FREE'),('fence_generation',True)]:
            with self.assertRaises(ValidationError):validator('PendingPublicationState').validate({**pending,field:value})

class BridgeLifecycleTests(unittest.TestCase):
    def test_logout_and_switch_revoke_all_proof_classes_retain_receipt(self):
        for event in ['logout','account_switch','security_revoke']:
            b=BridgeModel();original=copy.deepcopy(b.receipt)
            self.assertEqual(b.transition(event),'REVOKED')
            epoch=b.epoch
            for repeat in [event,'session_expiry','cutover','logout']:
                self.assertEqual(b.transition(repeat),'REVOKED');self.assertEqual(b.epoch,epoch)
            for proof in ['S','B','T','F']:
                with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay(proof,actor='alice',epoch=epoch)
            self.assertEqual(b.receipt,original);self.assertIsNone(b.session);self.assertTrue(b.ticket_revoked)

    def test_natural_expiry_and_cutover_detach_then_explicit_bound_recovery(self):
        for event,proof,actor in [('session_expiry','B',None),('cutover','F','alice')]:
            b=BridgeModel();b.transition(event);epoch=b.epoch
            self.assertEqual(b.transition(event),'DETACHED');self.assertEqual(b.epoch,epoch)
            with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay('S',actor='alice',epoch=epoch)
            self.assertEqual(b.replay(proof,actor=actor,epoch=epoch,rebind=True),(201,'original-safe-bytes'))
            self.assertEqual(b.state,'ACTIVE');self.assertEqual(b.sessions_minted,1)
            newepoch=b.epoch
            self.assertEqual(b.replay('S',actor='alice',epoch=newepoch,session=b.session),(201,'original-safe-bytes'))
            self.assertEqual(b.sessions_minted,1)

    def test_foreign_user_cannot_use_original_ticket_session_transfer_or_password(self):
        for state in ['ACTIVE','DETACHED']:
            for proof in ['S','B','T','F']:
                b=BridgeModel()
                if state=='DETACHED':b.transition('cutover')
                before=copy.deepcopy(b.__dict__)
                with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay(proof,actor='bob',epoch=b.epoch,password=True,rebind=True)
                self.assertEqual(b.__dict__,before)

    def test_ticket_alone_wrong_password_bootstrap_and_signature_are_denied(self):
        for kwargs in [{'proof':'T','original':False},{'proof':'T','ticket':False},{'proof':'B','password':False},
                       {'proof':'B','original':False},{'proof':'key-only'},{'proof':'T','ticket_version':2}]:
            b=BridgeModel();before=copy.deepcopy(b.__dict__)
            with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay(**kwargs)
            self.assertEqual(b.__dict__,before)

    def test_expired_ticket_independent_bootstrap_valid_until_bridge_window(self):
        b=BridgeModel();b.transition('session_expiry')
        with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay('T',epoch=b.epoch,now=95)
        self.assertEqual(b.replay('B',epoch=b.epoch,now=95),(201,'original-safe-bytes'))
        with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay('B',epoch=b.epoch,now=100)
        b.transition('replay_window_expiry');self.assertEqual(b.state,'EXPIRED')
        original=copy.deepcopy(b.receipt);epoch=b.epoch
        b.transition('cutover');b.transition('replay_window_expiry')
        self.assertEqual(b.epoch,epoch);self.assertEqual(b.receipt,original)

    def test_competing_rebind_and_superseded_ticket_session_epochs(self):
        b=BridgeModel();b.transition('cutover');old=b.epoch
        b.replay('F',actor='alice',epoch=old,rebind=True)
        after=copy.deepcopy(b.__dict__)
        with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay('F',actor='alice',epoch=old,rebind=True)
        self.assertEqual(b.__dict__,after);self.assertEqual(b.sessions_minted,1)
        with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay('T',actor='alice',epoch=b.epoch,ticket_version=1)
        self.assertEqual(b.replay('T',actor='alice',epoch=b.epoch,ticket_version=b.ticket_version),(201,'original-safe-bytes'))

    def test_repeated_same_user_login_rotates_without_changing_receipt(self):
        b=BridgeModel();original=copy.deepcopy(b.receipt);old=b.session
        for _ in range(2):
            new=b.repeat_login('alice');self.assertNotEqual(old,new);old=new
        with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay('S',actor='alice',epoch=1)
        self.assertEqual(b.receipt,original);self.assertEqual(b.sessions_minted,0)

    def test_changed_body_key_cannot_rebind_or_replay_receipt(self):
        for kwargs in [{'digest':'new-body'},{'key':'other-key'}]:
            b=BridgeModel();before=copy.deepcopy(b.__dict__)
            with self.assertRaisesRegex(Denied,'IDEMPOTENCY_CONFLICT'):b.replay('B',rebind=True,**kwargs)
            self.assertEqual(b.__dict__,before)

    def test_all_transition_orders_preserve_revocation_and_receipt_truth(self):
        for events in itertools.permutations(['logout','account_switch','session_expiry','cutover']):
            b=BridgeModel();original=copy.deepcopy(b.receipt)
            for event in events:b.transition(event)
            self.assertEqual(b.state,'REVOKED');self.assertTrue(b.ticket_revoked)
            self.assertEqual(b.receipt,original);self.assertEqual(b.sessions_minted,0)

    def test_unknown_ack_does_not_authorize_logout_retry_or_foreign_restore(self):
        table=load('receipt-bridge-lifecycle-v1.json')
        row=next(r for r in table['transitions'] if r['event']=='logout')
        self.assertEqual(row['unknown'],'GET me only; never blind logout retry')
        for committed in [False,True]:
            b=BridgeModel()
            if committed:b.transition('logout')
            # GET reconciliation is a read; observed session loss does not use receipt.
            before=copy.deepcopy(b.__dict__);status=401 if b.session is None else 200
            self.assertEqual(status,401 if committed else 200);self.assertEqual(before,b.__dict__)
            if committed:
                with self.assertRaises(Denied):b.replay('B',epoch=b.epoch,password=True)

    def test_private_bridge_schema_terminal_binding_negatives_and_transition_coverage(self):
        value={'bridge_id':'00000000-0000-4000-8000-000000000001','original_scope':'bootstrap:synthetic',
               'bootstrap_fingerprint':'a'*64,'receipt_owner_id':1,'session_binding':None,'revocation_epoch':2,
               'state':'REVOKED','session_lineage_id':'00000000-0000-4000-8000-000000000002','replay_until':'2026-10-16T00:00:00Z','ticket_version':2,
               'ticket_expires_at':None,'ticket_revoked':True,'transfer_binding':None}
        validator('ReceiptBridgeFacts').validate(value)
        for field,data in [('session_binding','old-session'),('ticket_revoked',False),('transfer_binding','foreign'),('password','private')]:
            with self.assertRaises(ValidationError):validator('ReceiptBridgeFacts').validate({**value,field:data})
        table=load('receipt-bridge-lifecycle-v1.json')
        self.assertEqual({r['event'] for r in table['transitions']},{'logout','account_switch','session_expiry','cutover','replay_window_expiry'})
        source=(ROOT/'users/views.py').read_text(encoding='utf-8')
        self.assertIn('django_logout(request)',source);self.assertIn('{"completed": True}',source)
        baseline=(ROOT/'users/tests/test_identity.py').read_text(encoding='utf-8')
        for name in ['test_register_lost_ack_replays_only_original_bootstrap','test_switch_user_flushes_previous_session','test_logout_invalidates_session_and_repeat_requires_auth']:
            self.assertIn(name,baseline)

    def test_cutover_checkpoint_repeats_do_not_revoke_recovered_target_session(self):
        b=BridgeModel();b.transition('cutover')
        b.replay('F',actor='alice',epoch=b.epoch,rebind=True)
        before=copy.deepcopy(b.__dict__)
        self.assertEqual(b.transition('cutover'),'ACTIVE')
        self.assertEqual(b.__dict__,before)
        with self.assertRaisesRegex(Denied,'STOP_WRITES'):b.transition('cutover',checkpoint='different')
        self.assertEqual(b.__dict__,before)

    def test_unknown_unverified_or_dual_writer_cutover_changes_no_authority(self):
        for kwargs in [{'drained':False},{'verified':False}]:
            b=BridgeModel();before=copy.deepcopy(b.__dict__)
            with self.assertRaisesRegex(Denied,'STOP_WRITES'):b.transition('cutover',**kwargs)
            self.assertEqual(b.__dict__,before)

    def test_inactive_owner_and_absent_transfer_binding_fail_closed(self):
        for proof in ['S','B','T','F']:
            b=BridgeModel();b.owner_active=False;before=copy.deepcopy(b.__dict__)
            with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay(proof,actor='alice')
            self.assertEqual(b.__dict__,before)
        b=BridgeModel();b.transfer=False
        with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay('F',actor='alice')

    def test_lost_all_cookies_replay_after_commit_needs_original_proof_and_password(self):
        b=BridgeModel();b.session=None;b.state='DETACHED';b.ticket_revoked=True
        self.assertEqual(b.replay('B',actor=None,password=True),(201,'original-safe-bytes'))
        # Lost the recovery Set-Cookie too: reread current epoch for EXPLICIT replay.
        self.assertEqual(b.replay('B',actor=None,password=True,epoch=b.epoch),(201,'original-safe-bytes'))
        self.assertEqual(b.sessions_minted,2)
        self.assertEqual(hashlib.sha256(json.dumps(b.receipt,sort_keys=True).encode()).hexdigest(),b.receipt_hash)

    def test_gate_descriptor_shapes_require_owner_and_pending_as_one_tuple(self):
        value={'namespace':'public','pending_operation_id':None,'owner_id':None,'fence_generation':3,'lease_until':None}
        validator('PublicationGateFacts').validate(value)
        for field,data in [('owner_id','00000000-0000-4000-8000-000000000001'),('lease_until','2026-10-09T00:00:00Z'),('fence_generation',True)]:
            with self.assertRaises(ValidationError):validator('PublicationGateFacts').validate({**value,field:data})
        with self.assertRaises(ValidationError):validator('PublicationGateFacts').validate({**value,'pending_operation_id':'00000000-0000-4000-8000-000000000001'})
        descriptor={'operation_id':'00000000-0000-4000-8000-000000000001','release_id':'initial','manifest_digest':'a'*64,'fence_generation':0}
        validator('ActiveReleaseDescriptor').validate(descriptor)
        with self.assertRaises(ValidationError):validator('ActiveReleaseDescriptor').validate({**descriptor,'owner_id':'private'})

    def test_logout_keeps_another_independent_same_owner_session_bridge(self):
        a,b=BridgeModel(),BridgeModel();b.session='session-B';b.lineage='lineage-B'
        untouched=copy.deepcopy(b.__dict__)
        for bridge in [a,b]:
            if bridge.lineage=='lineage-A':bridge.transition('logout')
        self.assertEqual(a.state,'REVOKED');self.assertEqual(b.__dict__,untouched)
        self.assertEqual(b.replay('S',actor='alice',session='session-B'),(201,'original-safe-bytes'))

    def test_session_proof_cannot_be_used_from_another_session_same_owner(self):
        b=BridgeModel();before=copy.deepcopy(b.__dict__)
        with self.assertRaisesRegex(Denied,'STATE_CONFLICT'):b.replay('S',actor='alice',session='different-session')
        self.assertEqual(b.__dict__,before)

if __name__=='__main__':unittest.main()
