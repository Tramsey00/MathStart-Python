"""T010 optimistic concurrency, bound to actor, authorization and record snapshot."""
import hashlib
import json
from backend.staff import reads
from backend.users.service import conflict
SALT='staff.t010.expected-revision.v1'

def snapshot(uow,resource,row,data=None):
    if data is None:data=reads.dto(uow,resource,row)
    if resource=='users':data={**data,'password_revision':hashlib.sha256(row.password.encode()).hexdigest()}
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def binding(uow,resource,row,scope,data=None):
    return {'actor':scope.user_id,'scope':scope.revision,'resource':resource,'id':row.id,'snapshot':snapshot(uow,resource,row,data)}

def issue(uow,resource,row,scope,signer,data):
    return signer.dumps(binding(uow,resource,row,scope,data),SALT)

def require_current(uow,resource,row,scope,signer,token):
    from backend.infrastructure.http.transport import APIError
    try:value=signer.loads(token,SALT,max_length=8192)
    except (APIError,TypeError,ValueError):raise conflict() from None
    if value!=binding(uow,resource,row,scope):raise conflict()
