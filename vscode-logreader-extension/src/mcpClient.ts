import * as net from 'net';
import { EventEmitter } from 'events';

export interface LogFile {
    path: string;
    content: string;
    truncated?: boolean;
    error?: string;
}

export interface LogResponse {
    files: LogFile[];
}

export class MCPClient extends EventEmitter {
    private socket: net.Socket | null = null;
    private messageBuffer: string = '';
    private requestId: number = 1;
    private callbacks: Map<number, (response: any) => void> = new Map();

    constructor(private processId: number) {
        super();
    }

    async connect(): Promise<void> {
        return new Promise((resolve, reject) => {
            this.socket = new net.Socket();
            
            this.socket.on('data', (data) => {
                this.handleData(data.toString());
            });

            this.socket.on('error', (error) => {
                console.error('Socket error:', error);
                this.emit('error', error);
            });

            this.socket.connect({ port: this.processId }, () => {
                console.log('Connected to MCP server');
                resolve();
            });
        });
    }

    private handleData(data: string) {
        this.messageBuffer += data;
        
        try {
            const message = JSON.parse(this.messageBuffer);
            this.messageBuffer = '';
            
            if (message.id && this.callbacks.has(message.id)) {
                const callback = this.callbacks.get(message.id)!;
                callback(message.result);
                this.callbacks.delete(message.id);
            }
        } catch (e) {
            // Incomplete message, wait for more data
        }
    }

    async getLogFiles(searchString: string = ''): Promise<LogResponse> {
        const requestId = this.requestId++;
        
        const request = {
            jsonrpc: '2.0',
            method: 'get_logfiles',
            params: { filename_search_string: searchString },
            id: requestId
        };

        return new Promise((resolve, reject) => {
            if (!this.socket) {
                reject(new Error('Not connected to MCP server'));
                return;
            }

            this.callbacks.set(requestId, (response) => {
                try {
                    const parsedResponse = JSON.parse(response);
                    resolve(parsedResponse);
                } catch (e) {
                    reject(e);
                }
            });

            this.socket.write(JSON.stringify(request) + '\n');
        });
    }

    disconnect() {
        if (this.socket) {
            this.socket.end();
            this.socket = null;
        }
    }
}