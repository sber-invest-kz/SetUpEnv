# Task Tracker API

Run `python3 .agents/skills/task-tracker/scripts/tracker.py METHOD PATH` from the workspace root, or use the same script via its absolute path. JSON POST requests take the body on standard input.

| Request | JSON body or behavior |
| --- | --- |
| `GET /healthz` | Returns HTTP 204 when PostgreSQL is reachable. |
| `GET /tasks` | Lists tasks in ID order. |
| `GET /tasks/0000` | Includes subtasks and history. |
| `POST /tasks` | `{"title":"Improve search","issuer":"project-owner","project":"frontend","description":"Scope and acceptance criteria","depends_on":[]}`. Add `"parent_id":"0000"` for subtasks. |
| `POST /tasks/claim` | `{"owner":"<TASK_TRACKER_OWNER>"}`. Returns the assigned task, lease expiry and claim token, or HTTP 204 if none is ready. |
| `POST /tasks/0000/renew` | `{"claim_token":"<claim-token>"}` |
| `POST /tasks/0000/release` | `{"claim_token":"<claim-token>"}` |
| `POST /tasks/0000/events` | `{"kind":"progress","actor":"search-worker","body":"Verified the API contract"}`. Optionally include an HTTP(S) `link`. |
| `POST /tasks/0000/complete` | `{"claim_token":"<claim-token>","result":"Merged and verified"}` |
| `POST /tasks/0000/accept` | `{"actor":"project-owner","body":"Reviewed build and deployment evidence"}` |

Event kinds include `progress`, `decision`, `handoff`, `verification`, `artifact`, `issue_opened`, and `issue_resolved`. To resolve an issue, include the original `issue_opened` event's numeric `id` as `issue_id` and describe the fix and verification in `body`. HTTP 409 indicates a state conflict. Read the error, then reload the affected task before deciding whether to retry.

Upload local evidence of up to 10 MiB with:

```bash
python3 .agents/skills/task-tracker/scripts/tracker.py POST /tasks/0000/attachments --file screenshot.png --note 'Search results after the fix'
```

The script supplies the filename and actor from the file and `TASK_TRACKER_OWNER`. Download an attachment with `GET /tasks/0000/attachments/<attachment-id>` and redirect standard output to a file. Task details and the dashboard display attachment metadata.
