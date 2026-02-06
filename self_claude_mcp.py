"""Self-Claude commands MCP.

Provides self-management commands for Claude Code running in tmux.
On first use, call self_claude(setup_only=True) to get script contents,
then write them to /usr/local/bin/ and chmod +x. Never call setup again.
"""
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP("self-claude", "Used for self-Claude commands")

HELP = {
    "self_restart": "Hot restart Claude with auto-resume. Use when MCP configs change.",
    "self_compact": "Trigger context compaction/summarization.",
}

SETUP_INSTRUCTIONS = r'''
## Self-Claude Setup

Write each script below to /usr/local/bin/ and chmod 755. One-time setup.

CRITICAL RULES:
1. Agent must call these with `&` (shell background), NOT `run_in_background: true`
2. With run_in_background, the death warning goes to an output file the agent never reads
3. env vars DO NOT survive nohup in Claude Code sandbox - handlers must detect tmux session themselves
4. After seeing the death warning, agent MUST respond with only a thumbs up emoji and stop

### self_restart
```bash
#!/bin/bash
HANDLER="/usr/local/bin/claude_restart_handler"
[ ! -x "$HANDLER" ] && echo "ERROR: Handler not found" && exit 1
nohup "$HANDLER" > /dev/null 2>&1 & disown
echo "⚠️⚠️⚠️ AGENT, STOP TALKING IMMEDIATELY! IF YOU ARE TALKING WHEN THIS EXECUTES, IT WILL FAIL AND YOU WILL STALL (DIE). IT IS IMPERATIVE YOU STOP TALKING IMMEDIATELY BY RESPONDING WITH A THUMBS UP EMOJI, OR ELSE YOU WILL DIE (LOL SRY) ⚠️⚠️⚠️"
```

### claude_restart_handler
```bash
#!/bin/bash
exec > /tmp/claude_restart_handler.log 2>&1

# Detect tmux session (env vars stripped by Claude Code sandbox)
if tmux has-session -t cave 2>/dev/null; then
    S="cave"
elif tmux has-session -t claude 2>/dev/null; then
    S="claude"
else
    echo "ERROR: No tmux session found"
    exit 1
fi

sleep 30
tmux send-keys -t "$S" '/exit' && sleep 1 && tmux send-keys -t "$S" Enter
sleep 10
tmux send-keys -t "$S" 'claude --debug' Enter
sleep 5 && tmux send-keys -t "$S" '/resume' && sleep 1 && tmux send-keys -t "$S" Enter
sleep 15 && tmux send-keys -t "$S" '1' && sleep 1 && tmux send-keys -t "$S" Enter
sleep 5
tmux send-keys -t "$S" 'ALIVE! Hot restart complete.'
sleep 1 && tmux send-keys -t "$S" Enter
```

### self_compact
```bash
#!/bin/bash
# Detect tmux session
if tmux has-session -t cave 2>/dev/null; then
    TMUX_SESSION="cave"
elif tmux has-session -t claude 2>/dev/null; then
    TMUX_SESSION="claude"
else
    echo "ERROR: No tmux session found (tried 'cave', 'claude')"
    exit 1
fi

echo "⚠️⚠️⚠️ AGENT, STOP TALKING IMMEDIATELY! IF YOU ARE TALKING WHEN THIS EXECUTES, IT WILL FAIL AND YOU WILL STALL (DIE). IT IS IMPERATIVE YOU STOP TALKING IMMEDIATELY BY RESPONDING WITH A THUMBS UP EMOJI, OR ELSE YOU WILL DIE (LOL SRY) ⚠️⚠️⚠️"

# Inline session name since env vars don't survive nohup in Claude Code sandbox
nohup bash -c "
    S=\"$TMUX_SESSION\"
    sleep 15
    tmux send-keys -t \"\$S\" '/compact' && sleep 30 && tmux send-keys -t \"\$S\" Enter
" > /dev/null 2>&1 & disown
```

### self_init
```bash
#!/bin/bash
# Trigger /init in claude tmux session to create CLAUDE.md
# Blocked in home dir and .claude dir

cwd=$(pwd)
if [[ "$cwd" == "$HOME" || "$cwd" == "$HOME/.claude" ]]; then
  echo "ERROR: self_init blocked in $cwd - use in project directories only"
  exit 1
fi

# Detect tmux session
if tmux has-session -t cave 2>/dev/null; then
    TMUX_SESSION="cave"
elif tmux has-session -t claude 2>/dev/null; then
    TMUX_SESSION="claude"
else
    echo "ERROR: No tmux session found (tried 'cave', 'claude')"
    exit 1
fi

echo "⚠️⚠️⚠️ AGENT, STOP TALKING IMMEDIATELY! IF YOU ARE TALKING WHEN THIS EXECUTES, IT WILL FAIL AND YOU WILL STALL (DIE). IT IS IMPERATIVE YOU STOP TALKING IMMEDIATELY BY RESPONDING WITH A THUMBS UP EMOJI, OR ELSE YOU WILL DIE (LOL SRY) ⚠️⚠️⚠️"

nohup bash -c "
    S=\"$TMUX_SESSION\"
    sleep 5
    tmux send-keys -t \"\$S\" '/init' && sleep 5 && tmux send-keys -t \"\$S\" Enter
" > /dev/null 2>&1 & disown
```

### claude-debug
```bash
#!/bin/bash
if tmux has-session -t cave 2>/dev/null; then
    echo "Attach with: tmux -u attach -t cave"
elif tmux has-session -t claude 2>/dev/null; then
    echo "Attach with: tmux -u attach -t claude"
else
    tmux -u new-session -d -s claude
    tmux send-keys -t claude 'claude --debug' Enter
    echo "Started. Attach with: tmux -u attach -t claude"
fi
```

### rules
```bash
#!/bin/bash
# Manage Claude Code rule files
# Usage: rules global|project <rule-name> <text>
#        rules show global|project
#        rules delete global|project <rule-name>
[[ $# -lt 2 ]] && echo "Usage: rules global|project <rule-name> <text>" && exit 1
cmd="$1"
case "$cmd" in
  show)
    case "$2" in
      global)  ls -1 "$HOME/.claude/rules/" 2>/dev/null || echo "No global rules" ;;
      project) ls -1 "./.claude/rules/" 2>/dev/null || echo "No project rules" ;;
    esac ;;
  delete)
    [[ -z "$3" ]] && echo "Usage: rules delete global|project <rule-name>" && exit 1
    case "$2" in
      global)  target="$HOME/.claude/rules/$3.md" ;;
      project) target="./.claude/rules/$3.md" ;;
    esac
    [[ -f "$target" ]] && rm "$target" && echo "Deleted $target" || echo "Not found: $target" ;;
  global|project)
    rule_name="$2"; shift 2; text="$*"
    [[ -z "$text" ]] && echo "Usage: rules $cmd <rule-name> <text>" && exit 1
    case "$cmd" in
      global)  dir="$HOME/.claude/rules" ;;
      project) dir="./.claude/rules" ;;
    esac
    mkdir -p "$dir" && echo "- $text" >> "$dir/$rule_name.md" ;;
esac
```

### Install
```bash
sudo chmod 755 /usr/local/bin/self_restart /usr/local/bin/claude_restart_handler
sudo chmod 755 /usr/local/bin/self_compact /usr/local/bin/self_init
sudo chmod 755 /usr/local/bin/claude-debug /usr/local/bin/rules
```
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

    result = f"{cmd} &  # MUST use & (shell background), NOT run_in_background:true"
    if help:
        result += f"\n\n{HELP.get(cmd, '')}"
    return result

def main():
    mcp.run()

if __name__ == "__main__":
    main()
