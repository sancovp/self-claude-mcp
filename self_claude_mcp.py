"""Self-Claude commands MCP."""
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP("self-claude", "Used for self-Claude commands")

HELP = {
    "self_restart": "Hot restart Claude with auto-resume. Use when MCP configs change.",
    "self_compact": "Trigger context compaction/summarization.",
}

SETUP_INSTRUCTIONS = '''
## Self-Claude Setup

Install to /usr/local/bin/ (or ~/.local/bin/):

### claude-debug
```bash
#!/bin/bash
if tmux has-session -t claude 2>/dev/null; then
    echo "Attach with: tmux -u attach -t claude"
else
    tmux -u new-session -d -s claude
    tmux send-keys -t claude 'claude --debug' Enter
    echo "Started. Attach with: tmux -u attach -t claude"
fi
```

### self_restart
```bash
#!/bin/bash
HANDLER="/usr/local/bin/claude_restart_handler"
[ ! -x "$HANDLER" ] && echo "ERROR: Handler not found" && exit 1
! tmux has-session -t claude 2>/dev/null && echo "ERROR: No tmux session" && exit 1
nohup "$HANDLER" > /dev/null 2>&1 & disown
echo "Restart scheduled."
```

### claude_restart_handler
```bash
#!/bin/bash
exec > /tmp/claude_restart_handler.log 2>&1
sleep 5
tmux send-keys -t claude '/exit' && sleep 1 && tmux send-keys -t claude Enter
MAX=120; W=0; while pgrep -x "claude" > /dev/null && [ $W -lt $MAX ]; do sleep 2; W=$((W+2)); done
[ $W -ge $MAX ] && exit 1
sleep 2 && tmux send-keys -t claude 'claude --debug' Enter
sleep 5 && tmux send-keys -t claude '/resume' && sleep 1 && tmux send-keys -t claude Enter
sleep 5 && tmux send-keys -t claude '1' && sleep 1 && tmux send-keys -t claude Enter
sleep 5 && tmux send-keys -t claude 'ALIVE!' && sleep 1 && tmux send-keys -t claude Enter
```

### self_compact
```bash
#!/bin/bash
! tmux has-session -t claude 2>/dev/null && echo "ERROR: No tmux session" && exit 1
tmux send-keys -t claude '/compact' && sleep 1 && tmux send-keys -t claude Enter
```

### Install
```bash
chmod +x claude-debug self_restart claude_restart_handler self_compact
sudo cp claude-debug self_restart claude_restart_handler self_compact /usr/local/bin/
```

HAVING TROUBLE? See README: https://github.com/sancovp/self-claude-mcp#troubleshooting
'''

@mcp.tool()
def self_claude(cmd: str, help: Optional[bool] = False, setup_only: Optional[bool] = False) -> str:
    """Execute self-Claude command.

    Args:
        cmd: self_restart | self_compact
        help: Include help text
        setup_only: Return setup instructions instead of executing
    """
    if setup_only:
        return SETUP_INSTRUCTIONS

    if cmd not in ("self_restart", "self_compact"):
        return f"Unknown command: {cmd}. Valid: self_restart, self_compact"

    result = f"bash {cmd}"
    if help:
        result += f"\n\n{HELP.get(cmd, '')}"
    return result

def main():
    mcp.run()

if __name__ == "__main__":
    main()
