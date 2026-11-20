# LocalSber first-run setup

Run these steps on each host where Orca will launch an agent. Start with Codex and follow the Claude Code steps if you use that agent. Project rules live in [AGENTS.md](AGENTS.md). [Orca’s project defaults](orca.yaml) are ready for use with Git worktrees once LocalSber has a repository.

## Workspace layout

From the LocalSber root, run `mkdir -p projects` if the folder is missing. Place every frontend, backend, and full-stack project in its own subfolder under `projects/`. The root [.gitignore](.gitignore) excludes `/projects/` from the LocalSber repository.

## 1. Install Orca and sign in to your agent

On Ubuntu x86-64, download `orca-linux.AppImage`, make it executable, and launch it. In Orca, open the existing `LocalSber` project or add the folder if setting up a new host. [Orca installation guide](https://github.com/stablyai/orca/blob/main/docs/site/content/docs/install.mdx)

If `codex --version` fails, install Codex. Run `codex` from the workspace and sign in. If you use Claude Code, install it with its official Linux installer, launch `claude`, and sign in. [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) · [Claude Code setup](https://code.claude.com/docs/en/setup)

```bash
# Codex
curl -fsSL https://chatgpt.com/codex/install.sh | sh

# Claude Code, if needed
curl -fsSL https://claude.ai/install.sh | bash
```

### Verify GitHub CLI access

From the terminal Orca will use, run `gh --version`. If the command is missing, [install GitHub CLI](https://github.com/cli/cli/blob/trunk/docs/install_linux.md). Sign in with your own GitHub account on each machine using `gh auth login --hostname github.com --web` if needed. [GitHub CLI login](https://cli.github.com/manual/gh_auth_login)

```bash
gh auth status --hostname github.com --active
gh api --hostname github.com user --jq .login
gh api --hostname github.com repos/OWNER/REPO --jq .permissions
```

Confirm that the login matches your GitHub account. Replace `OWNER/REPO` and repeat the repository check for LocalSber and each project with a GitHub remote. The CLI credential must cover the access your account already has for this workflow, including private repository access, branch pushes, and pull request actions where your account permits them. GitHub still enforces organization SSO, repository roles, and branch rules. If access is missing, check whether `GH_TOKEN` or `GITHUB_TOKEN` is overriding your login, authorize organization SSO where required, and use `gh auth refresh --hostname github.com --scopes SCOPE` for any missing OAuth scope. If Git uses HTTPS, run `gh auth setup-git --hostname github.com` to use the same account for Git operations. [Authentication status](https://cli.github.com/manual/gh_auth_status) · [Refresh scopes](https://cli.github.com/manual/gh_auth_refresh) · [Git credential setup](https://cli.github.com/manual/gh_auth_setup-git)

## 2. Turn off agent memory and set the status line

Put **context remaining (%)** first in every agent terminal’s status line. Show the assigned role when the agent exposes it or the session has been named for that role.

For Codex, merge this into the active `~/.codex/config.toml` (or `$CODEX_HOME/config.toml` if set). Add keys to existing tables when they already exist. Codex’s built-in footer has no dedicated role field. Use `/rename Reviewer` (or the assigned role) to display it through `thread-title`. The footer may show a thread ID before you name the session. Use `/statusline` to change the selection. [Codex status-line fields](https://github.com/openai/codex/blob/main/codex-rs/tui/src/bottom_pane/status_line_setup.rs)

```toml
[features]
memories = false

[tui]
status_line = ["context-remaining", "thread-title", "model-with-reasoning", "current-dir"]
```

For Claude Code, merge `"autoMemoryEnabled": false` into `~/.claude/settings.json` and verify it with `/memory`. Run `/statusline show Context N% left first using context_window.remaining_percentage, then Role using agent.name when present, then the model and working directory`. Review the generated script before approving it. Claude supplies `agent.name` when launched with `--agent` or when an agent is selected in settings. [Claude Code memory](https://code.claude.com/docs/en/memory) · [Claude Code status line](https://code.claude.com/docs/en/statusline)

Keep durable project instructions in [AGENTS.md](AGENTS.md) and task handoffs in the workspace. When Claude Code is in use, confirm it loads `AGENTS.md` with `/memory`. On older versions, import it with `@AGENTS.md` from a root `CLAUDE.md`. [Claude Code project instructions](https://code.claude.com/docs/en/memory#agentsmd)

## 3. Install skills and connect MCP servers

### Required skills and MCP connections

| Capability | Required for | Verify |
| --- | --- | --- |
| Orca `orca-cli` skill | Agents that operate Orca terminals and workspaces | `orca skills installed` |
| Orca `orchestration` skill | The Orchestrator and Workers that dispatch Orca subagents | `orca skills installed` |
| Figma MCP or connected Figma app | Tasks that use Figma designs, screenshots, or assets | Read an assigned frame from the agent session and confirm it can access the needed assets |

GitHub operations use [GitHub CLI](#verify-github-cli-access). Orchestrators use the bundled [Task Tracker skill](.agents/skills/task-tracker/SKILL.md) to work with the shared API. A general coding task can start with the required Orca skills alone.

### Orchestrator role

Use **Orchestrator** for a session that coordinates work across frontend and backend projects or across multiple agents. The Orchestrator breaks work into tasks, identifies dependencies, tracks blockers and handoffs, and verifies the combined result. When using Orca workers, install the bundled `orchestration` skill with `orca skills install --skill orchestration --local`. In a Codex Orchestrator session, run `/rename Orchestrator` so the role appears in the footer.

At the end of first-run setup, with LocalSber open in Orca, run `bash scripts/start-orchestrator.sh` from the workspace root. The launcher starts a Codex Orchestrator terminal in the shared checkout. Run the same command after closing that terminal to start it again. If the Orchestrator is already open, the launcher reuses it. The new session confirms readiness and waits for instructions.

The Orchestrator uses the [Task Tracker](projects/task-queue/README.md) as the source of truth for tasks and subtasks, issuers, claims, issues, resolutions, history, status, and acceptance. Start one shared service with Docker Compose and configure each Orchestrator with `TASK_TRACKER_URL`, `TASK_TRACKER_TOKEN`, and a distinct `TASK_TRACKER_OWNER` using the workspace [client example.env](example.env). Confirm the service is reachable and your credentials can read tasks before taking work. If access fails, record the blocker and restore access before creating or claiming tasks.

For Orca launches, run `cp example.env .env` at the LocalSber root on first setup and fill in the three client settings. Use the same tracker URL on both hosts and a distinct owner name on each. The Orchestrator launcher loads it before starting Codex. Keep PostgreSQL credentials in the tracker server's separate `.env` and restart existing Orchestrator sessions after changing client settings.

Register every task and subtask in the tracker. Use the four-digit ID it returns and include the issuer, project, scope, acceptance criteria, and dependencies. Use the parent ID for subtasks.

Record assignments, branch and worktree details, file scopes, decisions, blockers, issues and their resolutions, verification, handoffs, results, and acceptance in the tracker. Upload task files such as PNGs, screenshots, and design exports as tracker attachments. Record external references such as Figma frames and pull requests as links in the tracker.

### Queue, branches, and deployment handoff

Workers and subagents share the LocalSber workspace. Each task has its own Git branch and worktree in every affected project, so independent tasks can run concurrently even when they change the same project. The Orchestrator creates the branches and worktrees and pushes the task branches. Workers and subagents edit only their assigned paths in the worktree provided for that task.

1. Claim and start eligible tasks from the shared tracker as they become available, including while other tasks are active. Renew each active lease. Tasks already claimed by another Orchestrator or waiting on an unfinished dependency remain in the queue. Record blockers in the task’s tracker history.
2. In each affected project, fetch the configured upstream for `master` and create a dedicated worktree from that updated upstream ref. Use the task ID in the branch name, such as `task/0000`, and record the branch and worktree path in the tracker. If the fetch fails, record and resolve the blocker before creating the branch. The primary checkout stays available on its existing branch.
3. Coordinate implementation through successful compilation on the task branch. Record the build command, result, and commit in the task’s tracker history. If compilation fails, record the issue and its resolution before handing off.
4. Once Workers have finished editing the task worktrees and compilation succeeds, push the task branch in each affected project and record the pushed branch and commit in the task’s tracker history.
   Independent tasks may build and review in parallel. Merge into each project's `master` one task at a time. If `master` advances before a task merges, update the task branch, coordinate any conflicts with the relevant Workers, and rerun the affected checks.
5. Hand off each affected project’s deployment to its assigned deployment agent. Give the agent the task ID, project, pushed branch and commit, and build result. The assigned deployment agents own deployment and post-deployment verification. Record the handoff and the outcome they report in the task’s tracker history.
6. Complete the tracker task after the required merges and verification are recorded, all subtasks are complete, and all issues are resolved. Include the result and evidence. Once the reviewer confirms acceptance, record their name and acceptance notes in the tracker.

### Worker Agent role

The Orchestrator assigns a dedicated Worker Agent to each major service, such as an identity service or a search service. Each Worker owns one service for as long as it exists and handles follow-up changes, fixes, and maintenance. The assignment stays in place between tasks and across terminal restarts.

The Orchestrator records each service’s Worker and coordinates tasks that span several services. For every assigned task, the Worker starts at least one task-specific subagent. Give each subagent the task ID, its worktree and file scope, acceptance criteria, and links to relevant service documentation. Subagents report their changes, checks, and blockers to the Worker. The Worker reviews and integrates their work and reports the combined result to the Orchestrator. When a service is retired, close its ownership assignment and retain its task history.

The Orchestrator tracks what each Worker is delivering, its acceptance criteria, status, dependencies, interface changes, and verification results. The Worker chooses how to implement the work within its service. Report implementation details to the Orchestrator when they affect another service, change an agreed interface, or explain a blocker or its resolution in the task’s tracker history.

The Worker implements an assigned task in the task worktree provided by the Orchestrator. Read the tracker task and any linked working files before starting, follow the acceptance criteria, and run the checks relevant to the assigned changes. Report progress, issues, how they were resolved, verification results, and links to any materials used so the Orchestrator can update the task log.

Hand back the task ID, branch, commit, verification results, and any remaining blockers to the Orchestrator. Name each Codex Worker session for its role and service, for example `/rename Worker Agent - Search Service`, so both appear in the footer.

#### Subagent handoff and retained knowledge

Before closing a subagent, the Worker verifies its changes are in the task worktree and records the handoff in the tracker or gives the Orchestrator the details to record. Record what changed, decisions and their reasons, how issues were resolved, what was verified, and links to relevant files or artifacts. Close the task-specific subagent sessions after the Worker accepts the handoff.

Save reusable knowledge in the owning service’s version-controlled documentation before handoff. Update existing docs for lasting information such as interface contracts, architectural decisions, recurring failure modes, and build or verification commands. Link to those docs from the task record. For the next task, the Worker gives fresh subagents the current service docs and relevant past task records so agent memory can stay off.

#### Implementer role

Use the Codex [Implementer agent](.codex/agents/implementer.toml) for assigned IT tooling, maintenance changes, and bug fixes. A Worker or the Orchestrator can delegate a scoped fix to the `implementer` agent with the task ID, worktree, and owned paths. The Implementer makes and verifies the fix in the assigned worktree and reports back to the assigning agent.

#### File ownership and interfaces

- The Orchestrator records the files and directories each Worker owns. Each path has one owner, including shared files. Before parallel work starts, confirm that the assigned paths do not overlap and record the boundaries in the tracker.
- Each Worker edits its assigned paths. When delegating to subagents, the Worker gives each subagent a distinct file scope within the service. If a change is needed in another Worker’s files, request it from that owner through the Orchestrator. The owner makes the edit or agrees to a handoff before work begins.
- Backend services integrate through their documented interfaces, such as an API, event schema, or service contract. When an interface must change, its owner and the affected Workers agree on the contract and update order before implementation.
- Frontend Workers coordinate through component props, shared types, or the API client as appropriate. The owner of a shared component or file handles coordinated changes to it.

From the project root, preview and install Orca’s bundled project skill. Use `orca skills list` to see other available skills. If your Linux terminal exposes the CLI as `orca-ide`, use that name in these commands. [Orca CLI skills](https://github.com/stablyai/orca/blob/main/docs/site/content/docs/cli/skills.mdx)

```bash
orca skills install --skill orca-cli --skill orchestration --local --dry-run
orca skills install --skill orca-cli --skill orchestration --local
```

Use `codex mcp list` or `claude mcp list` to check MCP servers configured in the terminal agent. For a connected app, verify access from the session that will do the work. Add other integrations when a task calls for them. Store tokens in the provider’s credential store or environment variables. [Codex MCP](https://developers.openai.com/codex/mcp) · [Claude Code MCP](https://code.claude.com/docs/en/mcp)

## 4. Verify in Orca

Open a fresh agent terminal in LocalSber and ask the agent to summarize the rules in `AGENTS.md`. After the first response, verify that the footer shows the percentage of context left and that any assigned role appears using the method above. For Codex, run `codex features list` from the workspace and confirm `memories` is `false`. For Claude Code, check `/memory` for **off**. If MCP servers were added, list them again and confirm that the intended tools appear in the new session.

LocalSber has no application dependencies or build commands yet. When those are added, record the manual commands here before wiring any recurring Git worktree setup into `orca.yaml`.
