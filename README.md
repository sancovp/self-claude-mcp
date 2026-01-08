# self-claude-mcp

> **Requires [Claude Code](https://claude.ai/download) | [SIGN UP HERE](https://claude.ai/)**

MCP server for Claude Code self-management commands (hot restart, compaction).

## Installation

```bash
pip install self-claude-mcp
```

Add to your Claude MCP config:

```json
{
  "mcpServers": {
    "self-claude": {
      "command": "self-claude-mcp"
    }
  }
}
```

## Setup

After installing the MCP, Claude needs to install bash scripts for the commands to work.

Ask Claude to run:
```
Use self_claude with setup_only=True and install the scripts
```

Or manually: call `self_claude(cmd="", setup_only=True)` to get the installation instructions.

## Requirements

- **tmux**: Scripts use tmux for session management
- **Claude Code**: Must be running inside a tmux session named "claude"

### Starting Claude in tmux

Use `claude-debug` (installed by setup) or manually:

```bash
tmux -u new-session -d -s claude
tmux send-keys -t claude 'claude --debug' Enter
tmux -u attach -t claude
```

## Usage

Once set up, Claude can use these commands:

| Command | Description |
|---------|-------------|
| `self_claude("self_restart")` | Hot restart with auto-resume |
| `self_claude("self_compact")` | Trigger context compaction |
| `self_claude("", setup_only=True)` | Get installation instructions |

### Hot Restart

Use when MCP configs change and you need to reload without losing conversation:

1. Claude calls `self_claude("self_restart")` → returns `bash self_restart`
2. Claude runs `bash self_restart`
3. Handler sends `/exit`, waits for death, relaunches, sends `/resume`, selects session 1

### Compaction

Use when context is running low:

1. Claude calls `self_claude("self_compact")` → returns `bash self_compact`
2. Claude runs `bash self_compact`
3. Sends `/compact` to the tmux session

## Troubleshooting

### "No tmux session 'claude'"

Make sure Claude Code is running inside a tmux session named "claude":
```bash
tmux -u new-session -s claude
claude --debug
```

### "Handler not found"

Run the setup instructions again:
```
self_claude(cmd="", setup_only=True)
```
Then install the scripts to `/usr/local/bin/`.

### Restart hangs

Check the handler log:
```bash
cat /tmp/claude_restart_handler.log
```

Common issues:
- `pgrep -x "claude"` matches wrong process → verify with `pgrep -x "claude"`
- tmux session died → restart with `claude-debug`

### Docker / Container

If running in a container, make sure:
- tmux is installed: `apt install tmux`
- Scripts are in PATH: `/usr/local/bin/` or `~/.local/bin/`
- Container user can write to `/tmp/`

## Scripts Installed

| Script | Location | Purpose |
|--------|----------|---------|
| `claude-debug` | `/usr/local/bin/` | Start Claude in tmux background |
| `self_restart` | `/usr/local/bin/` | Orchestrator (spawns handler) |
| `claude_restart_handler` | `/usr/local/bin/` | Detached handler (does actual restart) |
| `self_compact` | `/usr/local/bin/` | Trigger compaction |

## Security Note

⚠️ **Warning:** You should disallow this MCP on subagents. Subagents running these commands can cause strange interactions.

## License

MIT
