---
name: task-tracker
description: Operate the shared LocalSber Task Tracker when creating or claiming tasks, coordinating subtasks, recording issues and resolutions, uploading evidence, or completing and accepting work.
---

# LocalSber Task Tracker

Use the tracker as the source of truth for task records. The workspace root `example.env` describes the client settings. The Orca launcher exports them from the root `.env`. If working from another terminal, load that trusted local file using `set -a; . ./.env; set +a` from the workspace root. Check access before creating or claiming work. Never copy tracker or lease tokens into records or handoffs.

Use the bundled [tracker client](scripts/tracker.py) with Python 3. From the workspace root:

```bash
python3 .agents/skills/task-tracker/scripts/tracker.py GET /tasks
python3 .agents/skills/task-tracker/scripts/tracker.py GET /tasks/0000
```

For a JSON POST, pipe the JSON body to the client. Read the [API quick reference](references/api.md) when choosing an endpoint or writing a payload. A successful claim with no eligible work returns HTTP 204 and an empty body.

Use the ID returned by the tracker. Use `parent_id` for subtasks and `depends_on` for prerequisites. Claim as `TASK_TRACKER_OWNER`, renew the claim before its ten-minute expiry, and stop work under a claim rejected as stale. On a timed-out create, check the tracker before retrying to avoid duplicate tasks.

Record decisions, progress, handoffs, evidence, verification, and issue resolutions as history events. Link Figma frames and pull requests. Upload local evidence to the tracker as an attachment. Complete with verified results after subtasks and issues are closed. Record who accepted the result after the reviewer confirms acceptance. Follow the workspace setup guide for branch, deployment, and ownership responsibilities.
