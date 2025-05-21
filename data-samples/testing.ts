export interface TestItem {
  id: string;
  name: string;
  type: 'microservice' | 'function' | 'test-case';
  children?: TestItem[];
  // Additional properties for microservices
  projectId?: string;
  status?: 'online' | 'offline';
  version?: string;
  lastDeployed?: string;
}

export interface TestOutput {
  status: 'success' | 'failure';
  time: string;
  output: string;
  coverage: number;
  timestamp: string;
}

export interface TestMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}
