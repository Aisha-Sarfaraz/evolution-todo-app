#!/usr/bin/env node

/**
 * Simple test script for SpecifyPlus MCP Server
 *
 * This script sends MCP protocol requests to the server and validates responses.
 * Run this after building the server to verify it works correctly.
 *
 * Usage:
 *   node test.mjs
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class MCPTester {
  constructor() {
    this.serverProcess = null;
    this.responseBuffer = '';
  }

  async startServer() {
    return new Promise((resolve, reject) => {
      console.log('🚀 Starting MCP server...\n');

      const serverPath = join(__dirname, 'dist', 'index.js');
      this.serverProcess = spawn('node', [serverPath], {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.serverProcess.stderr.on('data', (data) => {
        const message = data.toString();
        console.log('  Server:', message.trim());

        if (message.includes('SpecifyPlus MCP Server running')) {
          resolve();
        }
      });

      this.serverProcess.on('error', reject);

      // Timeout after 5 seconds
      setTimeout(() => reject(new Error('Server startup timeout')), 5000);
    });
  }

  async sendRequest(request) {
    return new Promise((resolve, reject) => {
      const requestStr = JSON.stringify(request) + '\n';

      const timeout = setTimeout(() => {
        reject(new Error('Request timeout'));
      }, 3000);

      this.serverProcess.stdout.once('data', (data) => {
        clearTimeout(timeout);
        try {
          const response = JSON.parse(data.toString().trim());
          resolve(response);
        } catch (error) {
          reject(new Error('Invalid JSON response: ' + data.toString()));
        }
      });

      this.serverProcess.stdin.write(requestStr);
    });
  }

  async testListPrompts() {
    console.log('\n📋 Test 1: List Prompts');
    console.log('  Request: prompts/list\n');

    const response = await this.sendRequest({
      jsonrpc: '2.0',
      id: 1,
      method: 'prompts/list',
      params: {}
    });

    if (!response.result || !response.result.prompts) {
      throw new Error('Invalid response structure');
    }

    const prompts = response.result.prompts;
    console.log(`  ✅ Found ${prompts.length} prompts:`);
    prompts.forEach(p => {
      console.log(`     - ${p.name}: ${p.description.substring(0, 60)}...`);
    });

    return prompts.length > 0;
  }

  async testGetPrompt() {
    console.log('\n📄 Test 2: Get Prompt (sp.specify)');
    console.log('  Request: prompts/get with arguments\n');

    const response = await this.sendRequest({
      jsonrpc: '2.0',
      id: 2,
      method: 'prompts/get',
      params: {
        name: 'sp.specify',
        arguments: {
          arguments: 'Add user authentication feature'
        }
      }
    });

    if (!response.result || !response.result.messages) {
      throw new Error('Invalid response structure');
    }

    const content = response.result.messages[0].content.text;

    // Verify $ARGUMENTS was replaced
    if (content.includes('$ARGUMENTS')) {
      throw new Error('$ARGUMENTS placeholder was not replaced');
    }

    if (!content.includes('Add user authentication feature')) {
      throw new Error('User arguments not found in prompt');
    }

    console.log('  ✅ Prompt retrieved successfully');
    console.log('  ✅ $ARGUMENTS replaced correctly');
    console.log(`  ✅ Prompt length: ${content.length} characters`);

    return true;
  }

  async testListTools() {
    console.log('\n🔧 Test 3: List Tools');
    console.log('  Request: tools/list\n');

    const response = await this.sendRequest({
      jsonrpc: '2.0',
      id: 3,
      method: 'tools/list',
      params: {}
    });

    if (!response.result || !response.result.tools) {
      throw new Error('Invalid response structure');
    }

    const tools = response.result.tools;
    console.log(`  ✅ Found ${tools.length} tools:`);
    tools.forEach(t => {
      console.log(`     - ${t.name}: ${t.description}`);
    });

    return tools.length > 0;
  }

  async testCallTool() {
    console.log('\n⚙️  Test 4: Call Tool (list_commands)');
    console.log('  Request: tools/call\n');

    const response = await this.sendRequest({
      jsonrpc: '2.0',
      id: 4,
      method: 'tools/call',
      params: {
        name: 'list_commands',
        arguments: {}
      }
    });

    if (!response.result || !response.result.content) {
      throw new Error('Invalid response structure');
    }

    const commands = JSON.parse(response.result.content[0].text);
    console.log(`  ✅ Retrieved ${commands.length} commands`);
    console.log('  Sample commands:');
    commands.slice(0, 3).forEach(cmd => {
      console.log(`     - ${cmd.name}`);
    });

    return commands.length > 0;
  }

  async cleanup() {
    if (this.serverProcess) {
      this.serverProcess.kill();
    }
  }

  async run() {
    try {
      await this.startServer();

      const results = {
        listPrompts: await this.testListPrompts(),
        getPrompt: await this.testGetPrompt(),
        listTools: await this.testListTools(),
        callTool: await this.testCallTool()
      };

      console.log('\n' + '='.repeat(50));
      console.log('📊 Test Results:');
      console.log('='.repeat(50));
      console.log(`  List Prompts:  ${results.listPrompts ? '✅ PASS' : '❌ FAIL'}`);
      console.log(`  Get Prompt:    ${results.getPrompt ? '✅ PASS' : '❌ FAIL'}`);
      console.log(`  List Tools:    ${results.listTools ? '✅ PASS' : '❌ FAIL'}`);
      console.log(`  Call Tool:     ${results.callTool ? '✅ PASS' : '❌ FAIL'}`);
      console.log('='.repeat(50));

      const allPassed = Object.values(results).every(r => r === true);

      if (allPassed) {
        console.log('\n✨ All tests passed! MCP server is working correctly.\n');
        process.exit(0);
      } else {
        console.log('\n❌ Some tests failed. Check the output above.\n');
        process.exit(1);
      }

    } catch (error) {
      console.error('\n❌ Test failed:', error.message);
      console.error(error.stack);
      process.exit(1);
    } finally {
      await this.cleanup();
    }
  }
}

// Run tests
const tester = new MCPTester();
tester.run();
