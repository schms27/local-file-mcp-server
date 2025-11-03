import * as vscode from 'vscode';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import { MCPClient, LogFile } from './mcpClient';

let mcpProcess: ChildProcess | null = null;
let mcpClient: MCPClient | null = null;

export async function activate(context: vscode.ExtensionContext) {
    // Create a new output channel
    const outputChannel = vscode.window.createOutputChannel('Log Reader');
    context.subscriptions.push(outputChannel);

    // Register the main command
    let disposable = vscode.commands.registerCommand('logreader.getLogfiles', async () => {
        try {
            if (!mcpProcess || !mcpClient) {
                // Start the MCP server if it's not running
                await startMCPServer(outputChannel);
            }

            if (!mcpClient) {
                throw new Error('Failed to initialize MCP client');
            }

            // Show input box for search string
            const searchString = await vscode.window.showInputBox({
                placeHolder: 'Enter filename search string (optional)',
                prompt: 'Search for log files'
            });

            // Show progress while fetching logs
            const logs = await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Fetching log files...',
                cancellable: false
            }, async () => {
                const client = mcpClient;
                if (!client) {
                    throw new Error('MCP client not initialized');
                }
                return await client.getLogFiles(searchString || '');
            });

            // Display results
            await displayLogs(logs.files, outputChannel);

        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error instanceof Error ? error.message : String(error)}`);
            outputChannel.appendLine(`Error: ${error instanceof Error ? error.stack : String(error)}`);
        }
    });

    context.subscriptions.push(disposable);

    // Register a command to clear the output
    context.subscriptions.push(vscode.commands.registerCommand('logreader.clearOutput', () => {
        outputChannel.clear();
    }));
}

async function startMCPServer(outputChannel: vscode.OutputChannel): Promise<void> {
    return new Promise((resolve, reject) => {
        try {
            const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
            const proc = spawn(pythonPath, [path.join(__dirname, '../../main.py')]);
            mcpProcess = proc;

            if (!proc.pid) {
                throw new Error('Failed to start MCP server - no process ID');
            }

            mcpClient = new MCPClient(proc.pid);

            if (!proc.stdout || !proc.stderr) {
                throw new Error('Failed to get process streams');
            }

            proc.stdout.on('data', (data: Buffer) => {
                outputChannel.appendLine(`MCP Server: ${data.toString()}`);
            });

            proc.stderr.on('data', (data: Buffer) => {
                outputChannel.appendLine(`MCP Server Error: ${data.toString()}`);
            });

            proc.on('error', (error: Error) => {
                outputChannel.appendLine(`MCP Server Error: ${error.message}`);
                reject(error);
            });
        } catch (error) {
            reject(error);
        }

        // Wait for the server to start and connect
        setTimeout(async () => {
            try {
                await mcpClient?.connect();
                resolve();
            } catch (error) {
                reject(error);
            }
        }, 1000);
    });
}

async function displayLogs(logs: LogFile[], outputChannel: vscode.OutputChannel) {
    if (logs.length === 0) {
        vscode.window.showInformationMessage('No log files found.');
        return;
    }

    // Create QuickPick items for each log file
    const items = logs.map(log => ({
        label: path.basename(log.path),
        description: log.path,
        detail: log.error ? `Error: ${log.error}` : `Size: ${log.content.length} bytes${log.truncated ? ' (truncated)' : ''}`,
        log
    }));

    const selected = await vscode.window.showQuickPick(items, {
        placeHolder: 'Select a log file to view',
        matchOnDescription: true,
        matchOnDetail: true
    });

    if (selected) {
        const doc = await vscode.workspace.openTextDocument({
            content: selected.log.content,
            language: 'log'
        });
        await vscode.window.showTextDocument(doc, { preview: false });
    }
}

export function deactivate() {
    if (mcpClient) {
        mcpClient.disconnect();
        mcpClient = null;
    }
    if (mcpProcess) {
        mcpProcess.kill();
        mcpProcess = null;
    }
}