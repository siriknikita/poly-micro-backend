interface ConfigSchemaField {
  type: 'string' | 'number' | 'select' | 'array' | 'cron' | 'expression' | 'command';
  label: string;
  default: string | number | boolean | string[];
  options?: string[];
}

export interface PipelineBlock {
  id: string;
  name: string;
  icon: string;
  description: string;
  category: 'triggers' | 'execution' | 'flow' | 'automation';
  configSchema: Record<string, ConfigSchemaField>;
}

export interface BlockInstance extends PipelineBlock {
  instanceId: string;
  position: { x: number; y: number };
  config: Record<string, string | number | boolean | string[]>;
}

export interface PipelineConnection {
  source: string;
  target: string;
  type: 'success' | 'failure' | 'loop';
}

export interface Pipeline {
  id: string;
  name: string;
  blocks: BlockInstance[];
  connections: PipelineConnection[];
  variables: Record<string, string>;
}
