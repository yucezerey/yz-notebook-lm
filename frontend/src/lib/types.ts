export interface Notebook {
  id: string;
  url: string;
  name: string;
  description: string;
  topics: string[];
  created_at: string;
  updated_at: string;
  use_count: number;
  last_used?: string;
}

export interface TaskResult {
  task_id: string;
  status: "queued" | "running" | "completed" | "failed";
  result?: string;
  error?: string;
  progress_messages: string[];
}

export interface WSMessage {
  type: "progress" | "completed" | "error";
  task_id: string;
  message?: string;
  progress?: number;
  result?: string;
  error?: string;
}
