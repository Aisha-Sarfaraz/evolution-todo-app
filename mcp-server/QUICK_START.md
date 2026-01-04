# SpecifyPlus MCP Server - Quick Start Guide

Get the SpecifyPlus MCP server running in 5 minutes.

## Step 1: Install Dependencies

```bash
cd mcp-server
npm install
```

## Step 2: Build the Server

```bash
npm run build
```

This compiles TypeScript to JavaScript in the `dist/` directory.

## Step 3: Test the Server

```bash
npm test
```

You should see output like this:

```
🚀 Starting MCP server...
  Server: 🚀 SpecifyPlus MCP Server starting...
  Server: ✅ Loaded 13 SpecifyPlus commands

📋 Test 1: List Prompts
  ✅ Found 13 prompts:
     - sp.specify: Create or update the feature specification...
     - sp.plan: Execute the implementation planning workflow...
     ...

📄 Test 2: Get Prompt (sp.specify)
  ✅ Prompt retrieved successfully
  ✅ $ARGUMENTS replaced correctly

🔧 Test 3: List Tools
  ✅ Found 2 tools:
     - list_commands
     - get_command_info

⚙️  Test 4: Call Tool (list_commands)
  ✅ Retrieved 13 commands

==================================================
📊 Test Results:
==================================================
  List Prompts:  ✅ PASS
  Get Prompt:    ✅ PASS
  List Tools:    ✅ PASS
  Call Tool:     ✅ PASS
==================================================

✨ All tests passed! MCP server is working correctly.
```

## Step 4: Connect to Claude Desktop

### 4.1 Find Your Config File

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

### 4.2 Get Absolute Path

Run this command from the **repository root** to get the absolute path:

**Windows (PowerShell):**
```powershell
echo (Get-Location).Path\mcp-server\dist\index.js
```

**macOS/Linux:**
```bash
echo "$(pwd)/mcp-server/dist/index.js"
```

### 4.3 Update Claude Desktop Config

Edit the config file and add:

```json
{
  "mcpServers": {
    "specifyplus": {
      "command": "node",
      "args": [
        "PASTE_ABSOLUTE_PATH_HERE"
      ],
      "env": {}
    }
  }
}
```

**Example (Windows):**
```json
{
  "mcpServers": {
    "specifyplus": {
      "command": "node",
      "args": [
        "D:\\gemini-cli\\practice\\hacathons\\todo-app\\mcp-server\\dist\\index.js"
      ],
      "env": {}
    }
  }
}
```

**Example (macOS):**
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

### 4.4 Restart Claude Desktop

Quit Claude Desktop completely and restart it.

## Step 5: Verify Connection

1. Open Claude Desktop
2. Look for a **hammer icon** (🔨) or **prompt selector** in the interface
3. Click it to see available prompts
4. You should see all SpecifyPlus commands:
   - `sp.specify`
   - `sp.plan`
   - `sp.tasks`
   - `sp.implement`
   - etc.

## Step 6: Use a Command

### Example: Create a Feature Spec

1. Select prompt: `sp.specify`
2. In the arguments field, enter:
   ```
   Add task priority feature with high, medium, and low priority levels
   ```
3. Click "Use Prompt"
4. Claude will receive the complete `sp.specify` command with your feature description injected

### Example: Generate Implementation Plan

After creating a spec:

1. Select prompt: `sp.plan`
2. Leave arguments empty (uses current branch context)
3. Click "Use Prompt"
4. Claude will generate the implementation plan

## Troubleshooting

### Commands Don't Appear in Claude Desktop

**Problem:** MCP server not showing up
**Solutions:**
1. Verify the absolute path in config is correct
2. Make sure you ran `npm run build`
3. Check that `dist/index.js` exists
4. Restart Claude Desktop completely (quit and reopen)

### Server Won't Start

**Problem:** Error when Claude Desktop tries to start server
**Solutions:**
1. Run `npm test` to see specific error
2. Check Node.js version: `node --version` (must be >= 18.0.0)
3. Verify `.claude/commands/` directory exists
4. Check server logs (Claude Desktop usually shows MCP server errors)

### $ARGUMENTS Not Replaced

**Problem:** Prompt still shows `$ARGUMENTS`
**Solutions:**
1. Make sure you're providing arguments when requesting the prompt
2. Check that the prompt is being requested via MCP (not manually copied)

## Next Steps

### Available Commands

Once connected, you have access to all SpecifyPlus workflow commands:

**Specification Phase:**
- `sp.specify` - Create feature specification
- `sp.clarify` - Ask clarification questions
- `sp.constitution` - Define project principles

**Planning Phase:**
- `sp.plan` - Generate implementation plan
- `sp.adr` - Document architectural decisions

**Execution Phase:**
- `sp.tasks` - Generate task breakdown
- `sp.checklist` - Create validation checklists
- `sp.implement` - Execute implementation

**Quality & Integration:**
- `sp.analyze` - Cross-artifact analysis
- `sp.git.commit_pr` - Git automation

**Utilities:**
- `sp.phr` - Record prompt history
- `sp.reverse-engineer` - Extract specs from code
- `sp.taskstoissues` - Convert tasks to GitHub issues

### Workflow Example

Complete feature development workflow:

1. **Create Spec:** Use `sp.specify` with feature description
2. **Clarify:** Use `sp.clarify` to resolve ambiguities
3. **Plan:** Use `sp.plan` to design architecture
4. **Document:** Use `sp.adr` for significant decisions
5. **Tasks:** Use `sp.tasks` to break down work
6. **Validate:** Use `sp.checklist` for quality checks
7. **Implement:** Use `sp.implement` to execute tasks
8. **Analyze:** Use `sp.analyze` for consistency
9. **Ship:** Use `sp.git.commit_pr` to commit and create PR

## Development Mode

If you're modifying the MCP server code:

```bash
# Terminal 1: Watch for changes
npm run dev

# Terminal 2: Test your changes
npm test

# After making changes, rebuild and restart Claude Desktop
```

## Support

- **Full Documentation:** See [README.md](README.md)
- **Agent Architecture:** See [../AGENTS.md](../AGENTS.md)
- **Project Documentation:** See [../.specify/README.md](../.specify/README.md)

## Success!

You now have SpecifyPlus commands available in any MCP-compatible environment. Use them to accelerate your Spec-Driven Development workflow! 🚀
