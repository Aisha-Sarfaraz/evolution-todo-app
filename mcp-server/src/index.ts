#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import * as fs from "fs/promises";
import * as path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

interface SpecifyPlusCommand {
  name: string;
  description: string;
  content: string;
  handoffs?: Array<{ label: string; agent: string; prompt?: string; send?: boolean }>;
  tools?: string[];
}

class SpecifyPlusMCPServer {
  private server: Server;
  private commands: Map<string, SpecifyPlusCommand> = new Map();
  private commandsDir: string;

  constructor() {
    this.server = new Server(
      {
        name: "specifyplus-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          prompts: {},
          tools: {},
        },
      }
    );

    // Find the .claude/commands directory
    // This assumes the server is running from mcp-server/dist/
    // and the .claude/commands directory is at the repo root
    this.commandsDir = path.resolve(__dirname, "../../.claude/commands");

    this.setupHandlers();
  }

  private async loadCommands(): Promise<void> {
    try {
      const files = await fs.readdir(this.commandsDir);
      const mdFiles = files.filter((f) => f.endsWith(".md"));

      for (const file of mdFiles) {
        const filePath = path.join(this.commandsDir, file);
        const content = await fs.readFile(filePath, "utf-8");

        // Extract frontmatter
        const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
        let description = "";
        let handoffs: Array<{ label: string; agent: string; prompt?: string; send?: boolean }> = [];
        let tools: string[] = [];

        if (frontmatterMatch) {
          const frontmatter = frontmatterMatch[1];
          const descMatch = frontmatter.match(/description:\s*(.+)/);
          if (descMatch) {
            description = descMatch[1].trim();
          }

          // Parse handoffs (if present)
          const handoffsMatch = frontmatter.match(/handoffs:\s*\n((?:\s+-\s+.+\n)+)/);
          if (handoffsMatch) {
            const handoffsText = handoffsMatch[1];
            const handoffBlocks = handoffsText.split(/\n\s+-\s+/).filter(Boolean);

            handoffs = handoffBlocks.map((block) => {
              const labelMatch = block.match(/label:\s*(.+)/);
              const agentMatch = block.match(/agent:\s*(.+)/);
              const promptMatch = block.match(/prompt:\s*(.+)/);
              const sendMatch = block.match(/send:\s*(.+)/);

              return {
                label: labelMatch ? labelMatch[1].trim() : "",
                agent: agentMatch ? agentMatch[1].trim() : "",
                prompt: promptMatch ? promptMatch[1].trim() : undefined,
                send: sendMatch ? sendMatch[1].trim() === "true" : undefined,
              };
            });
          }

          // Parse tools (if present)
          const toolsMatch = frontmatter.match(/tools:\s*\[([^\]]+)\]/);
          if (toolsMatch) {
            tools = toolsMatch[1].split(",").map((t) => t.trim().replace(/['"]/g, ""));
          }
        }

        const commandName = file.replace(/^sp\./, "").replace(/\.md$/, "");
        this.commands.set(commandName, {
          name: commandName,
          description: description || `${commandName} command`,
          content,
          handoffs,
          tools,
        });
      }

      console.error(`✅ Loaded ${this.commands.size} SpecifyPlus commands`);
    } catch (error) {
      console.error("❌ Error loading commands:", error);
      throw error;
    }
  }

  private setupHandlers(): void {
    // List available prompts
    this.server.setRequestHandler(ListPromptsRequestSchema, async () => {
      await this.loadCommands(); // Reload commands on each request for latest updates

      return {
        prompts: Array.from(this.commands.values()).map((cmd) => ({
          name: `sp.${cmd.name}`,
          description: cmd.description,
          arguments: [
            {
              name: "arguments",
              description: "Command arguments (replaces $ARGUMENTS in the prompt)",
              required: false,
            },
          ],
        })),
      };
    });

    // Get a specific prompt
    this.server.setRequestHandler(GetPromptRequestSchema, async (request) => {
      await this.loadCommands(); // Reload to ensure latest content

      const promptName = request.params.name.replace(/^sp\./, "");
      const command = this.commands.get(promptName);

      if (!command) {
        throw new Error(`Prompt not found: ${request.params.name}`);
      }

      // Get arguments from request
      const args = request.params.arguments || {};
      const userArguments = (args.arguments as string) || "";

      // Replace $ARGUMENTS placeholder with actual arguments
      const processedContent = command.content.replace(/\$ARGUMENTS/g, userArguments);

      // Build metadata
      const metadata: Record<string, unknown> = {
        command: `sp.${command.name}`,
        description: command.description,
      };

      if (command.handoffs && command.handoffs.length > 0) {
        metadata.handoffs = command.handoffs;
      }

      if (command.tools && command.tools.length > 0) {
        metadata.requiredTools = command.tools;
      }

      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: processedContent,
            },
          },
        ],
        description: `SpecifyPlus command: sp.${command.name}`,
        metadata,
      };
    });

    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "list_commands",
            description: "List all available SpecifyPlus commands with descriptions",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
          {
            name: "get_command_info",
            description: "Get detailed information about a specific SpecifyPlus command",
            inputSchema: {
              type: "object",
              properties: {
                command: {
                  type: "string",
                  description: "Command name (without 'sp.' prefix)",
                },
              },
              required: ["command"],
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      await this.loadCommands();

      const { name, arguments: args } = request.params;

      switch (name) {
        case "list_commands": {
          const commandList = Array.from(this.commands.values()).map((cmd) => ({
            name: `sp.${cmd.name}`,
            description: cmd.description,
            hasHandoffs: (cmd.handoffs?.length || 0) > 0,
            requiresTools: cmd.tools?.join(", ") || "none",
          }));

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(commandList, null, 2),
              },
            ],
          };
        }

        case "get_command_info": {
          const commandName = (args as { command: string }).command;
          const command = this.commands.get(commandName);

          if (!command) {
            return {
              content: [
                {
                  type: "text",
                  text: `Error: Command '${commandName}' not found`,
                },
              ],
              isError: true,
            };
          }

          const info = {
            name: `sp.${command.name}`,
            description: command.description,
            handoffs: command.handoffs || [],
            requiredTools: command.tools || [],
            contentPreview: command.content.substring(0, 500) + "...",
          };

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(info, null, 2),
              },
            ],
          };
        }

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async run(): Promise<void> {
    console.error("🚀 SpecifyPlus MCP Server starting...");
    console.error(`📂 Commands directory: ${this.commandsDir}`);

    // Load commands at startup
    await this.loadCommands();

    const transport = new StdioServerTransport();
    await this.server.connect(transport);

    console.error("✨ SpecifyPlus MCP Server running");
  }
}

// Start the server
const server = new SpecifyPlusMCPServer();
server.run().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
