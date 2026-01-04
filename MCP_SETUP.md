# SpecifyPlus MCP Server Setup

This document explains how to run the SpecifyPlus MCP server to make all Spec-Driven Development commands available to any MCP-compatible agent or IDE.

## What You Get

After setup, you'll have access to **all 13 SpecifyPlus commands** from any MCP-compatible environment:

- Claude Desktop
- VS Code (with MCP extension)
- Any custom agent that supports MCP protocol

Commands available:
- `sp.specify` - Create feature specifications
- `sp.clarify` - Ask clarification questions
- `sp.plan` - Generate implementation plans
- `sp.tasks` - Create task breakdowns
- `sp.implement` - Execute implementation
- `sp.adr` - Document architectural decisions
- `sp.analyze` - Cross-artifact analysis
- `sp.checklist` - Generate validation checklists
- `sp.constitution` - Define project principles
- `sp.phr` - Record prompt history
- `sp.git.commit_pr` - Git automation
- `sp.reverse-engineer` - Extract specs from code
- `sp.taskstoissues` - Convert tasks to GitHub issues

## Prerequisites

- Node.js >= 18.0.0
- npm (comes with Node.js)
- Claude Desktop (or another MCP-compatible client)

## Installation

### 1. Install Dependencies

```bash
cd mcp-server
npm install
```

### 2. Build the Server

```bash
npm run build
```

### 3. Test the Server

```bash
npm test
```

Expected output:
```
✨ All tests passed! MCP server is working correctly.
```

## Connecting to Claude Desktop

### Step 1: Get Absolute Path

From the **repository root**, run:

**Windows (PowerShell):**
```powershell
echo (Get-Location).Path\mcp-server\dist\index.js
```

**macOS/Linux:**
```bash
echo "$(pwd)/mcp-server/dist/index.js"
```

Copy the output - you'll need it in the next step.

### Step 2: Update Claude Desktop Config

**macOS:** Open `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** Open `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration (replace `PASTE_PATH_HERE` with the path from Step 1):

```json
{
  "mcpServers": {
    "specifyplus": {
      "command": "node",
      "args": [
        "PASTE_PATH_HERE"
      ],
      "env": {}
    }
  }
}
```

**Full Example (Windows):**
```json
{
  "mcpServers": {
    "specifyplus": {
      "command": "node",
      "args": [
        "D:\\projects\\todo-app\\mcp-server\\dist\\index.js"
      ],
      "env": {}
    }
  }
}
```

**Full Example (macOS):**
```json
{
  "mcpServers": {
    "specifyplus": {
      "command": "node",
      "args": [
        "/Users/yourname/projects/todo-app/mcp-server/dist/index.js"
      ],
      "env": {}
    }
  }
}
```

### Step 3: Restart Claude Desktop

Quit Claude Desktop completely and reopen it.

### Step 4: Verify

In Claude Desktop:
1. Look for prompt selector (usually a hammer 🔨 icon)
2. Click it
3. You should see all `sp.*` commands listed

## Usage Example

### Creating a Feature Specification

1. **In Claude Desktop**, select the `sp.specify` prompt
2. **In the arguments field**, enter your feature description:
   ```
   Add user authentication with email and password support
   ```
3. **Click "Use Prompt"**
4. Claude receives the complete command with your description injected

### Following the Workflow

After creating a spec, the command tells you the next step (handoff):

```
Next Step: Use sp.plan to create the implementation plan
```

Select `sp.plan` from the prompt selector and continue.

## Architecture

```
Repository Root
├── .claude/commands/          # Source: All SpecifyPlus commands
│   ├── sp.specify.md
│   ├── sp.plan.md
│   ├── sp.tasks.md
│   └── ... (13 total)
│
└── mcp-server/               # MCP Server
    ├── src/
    │   └── index.ts         # Server implementation
    ├── dist/                # Compiled output (npm run build)
    ├── package.json
    ├── README.md            # Full documentation
    └── QUICK_START.md       # Quick setup guide
```

### How It Works

1. **Server reads commands** from `.claude/commands/` on startup
2. **Exposes each as an MCP prompt** with metadata
3. **Accepts arguments** when prompt is requested
4. **Replaces `$ARGUMENTS`** placeholder with your input
5. **Returns complete prompt** ready for execution

## Advanced Configuration

### Running the Server Standalone

```bash
cd mcp-server
npm start
```

The server communicates via stdio (standard input/output) using the MCP protocol.

### Using with VS Code

If you have an MCP extension for VS Code, configure it similarly:

```json
{
  "mcp.servers": {
    "specifyplus": {
      "command": "node",
      "args": [
        "/absolute/path/to/mcp-server/dist/index.js"
      ]
    }
  }
}
```

### Development Mode

Watch for changes and auto-rebuild:

```bash
npm run dev
```

After code changes, rebuild and restart Claude Desktop to test.

## Troubleshooting

### "Server not found" or "Connection failed"

**Check:**
1. Absolute path in config is correct (no typos, uses forward or backward slashes correctly)
2. `dist/index.js` exists (run `npm run build` if missing)
3. Node.js version >= 18.0.0 (`node --version`)
4. Claude Desktop was completely restarted

**Fix:**
```bash
cd mcp-server
npm run build
# Then restart Claude Desktop
```

### Commands not showing in Claude Desktop

**Check:**
1. Config file syntax is valid JSON (no trailing commas, proper quotes)
2. Server is listed in Claude Desktop's MCP server list
3. No errors in Claude Desktop logs

**Fix:**
Open Claude Desktop logs (usually in settings) and check for MCP server errors.

### "$ARGUMENTS still appears in prompt"

This means arguments weren't passed properly.

**Check:**
1. You're using the prompt **via MCP** (not copy-pasting)
2. Arguments field was filled before clicking "Use Prompt"
3. Server is actually running (check Claude Desktop MCP status)

## Command Reference

### Governance & Quality
- `sp.constitution` - Define project principles and constraints
- `sp.analyze` - Cross-artifact consistency analysis
- `sp.checklist` - Generate validation checklists

### Specification Phase
- `sp.specify` - Create feature specification from natural language
- `sp.clarify` - Ask up to 5 targeted clarification questions

### Planning Phase
- `sp.plan` - Generate implementation plan with architecture
- `sp.adr` - Document architectural decision records

### Execution Phase
- `sp.tasks` - Generate dependency-ordered task breakdown
- `sp.implement` - Execute tasks from tasks.md

### Utilities
- `sp.phr` - Record prompt history for traceability
- `sp.reverse-engineer` - Extract specifications from existing code
- `sp.git.commit_pr` - Autonomous Git workflow execution
- `sp.taskstoissues` - Convert tasks to GitHub issues

## Support & Documentation

- **Quick Start:** [mcp-server/QUICK_START.md](mcp-server/QUICK_START.md)
- **Full MCP Documentation:** [mcp-server/README.md](mcp-server/README.md)
- **Agent Architecture:** [AGENTS.md](AGENTS.md)
- **Development Guide:** [CLAUDE.md](CLAUDE.md)

## Success!

You now have the complete SpecifyPlus workflow available in any MCP-compatible environment. Start with `sp.specify` to create your first feature specification! 🚀
