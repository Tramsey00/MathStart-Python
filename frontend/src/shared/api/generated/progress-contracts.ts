// Generated N012 read/self-report operation policy; no write-evidence operation.
export const progressOperations={
  "list_progress_skills": {
    "path": "/api/v1/progress/skills/",
    "method": "GET",
    "receipt": false,
    "request": null,
    "response": "SkillProgressListResponse"
  },
  "list_progress_topics": {
    "path": "/api/v1/progress/topics/",
    "method": "GET",
    "receipt": false,
    "request": null,
    "response": "TopicProgressListResponse"
  },
  "list_progress_events": {
    "path": "/api/v1/progress/events/",
    "method": "GET",
    "receipt": false,
    "request": null,
    "response": "ProgressEventListResponse"
  },
  "create_self_report": {
    "path": "/api/v1/progress/self-reports/",
    "method": "POST",
    "receipt": true,
    "request": "SelfReportRequest",
    "response": "SelfReportResultResponse"
  },
  "list_progress_completions": {
    "path": "/api/v1/progress/completions/",
    "method": "GET",
    "receipt": false,
    "request": null,
    "response": "CompletionHistoryListResponse"
  }
} as const;
