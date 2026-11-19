// Generated canonical Attempt types and operation policy.
import type {components} from './openapi';
export interface AttemptContracts {
create_attempt:{request:components['schemas']['CreateAttemptRequest'];response:components['schemas']['AttemptResponse']};
list_attempts:{request:never;response:components['schemas']['AttemptListResponse']};
get_attempt:{request:never;response:components['schemas']['AttemptResponse']};
update_draft:{request:components['schemas']['DraftUpdateRequest'];response:components['schemas']['AttemptResponse']};
submit_attempt:{request:components['schemas']['SubmitRequest'];response:components['schemas']['AttemptResponse']};
request_hint:{request:components['schemas']['HintRequest'];response:components['schemas']['HintResultResponse']};
reveal_attempt:{request:components['schemas']['RevealRequest'];response:components['schemas']['RevealResultResponse']};
abandon_attempt:{request:components['schemas']['AbandonRequest'];response:components['schemas']['AttemptResponse']};
}
export const attemptOperations={
  "create_attempt": {
    "path": "/api/v1/attempts/",
    "method": "POST",
    "receipt": true,
    "request": "CreateAttemptRequest",
    "response": "AttemptResponse"
  },
  "list_attempts": {
    "path": "/api/v1/attempts/",
    "method": "GET",
    "receipt": false,
    "request": null,
    "response": "AttemptListResponse"
  },
  "get_attempt": {
    "path": "/api/v1/attempts/{id}/",
    "method": "GET",
    "receipt": false,
    "request": null,
    "response": "AttemptResponse"
  },
  "update_draft": {
    "path": "/api/v1/attempts/{id}/draft/",
    "method": "PUT",
    "receipt": false,
    "request": "DraftUpdateRequest",
    "response": "AttemptResponse"
  },
  "submit_attempt": {
    "path": "/api/v1/attempts/{id}/submit/",
    "method": "POST",
    "receipt": true,
    "request": "SubmitRequest",
    "response": "AttemptResponse"
  },
  "request_hint": {
    "path": "/api/v1/attempts/{id}/hints/",
    "method": "POST",
    "receipt": true,
    "request": "HintRequest",
    "response": "HintResultResponse"
  },
  "reveal_attempt": {
    "path": "/api/v1/attempts/{id}/reveal/",
    "method": "POST",
    "receipt": true,
    "request": "RevealRequest",
    "response": "RevealResultResponse"
  },
  "abandon_attempt": {
    "path": "/api/v1/attempts/{id}/abandon/",
    "method": "POST",
    "receipt": true,
    "request": "AbandonRequest",
    "response": "AttemptResponse"
  }
} as const;
