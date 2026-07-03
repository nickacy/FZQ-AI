/**
 * V24 Contract Types
 * Must match backend DTOs exactly.
 */

// ── Execution ────────────────────────────────────────────────

export interface ExecutionResultV24 {
  intent: Record<string, any>;
  route: Record<string, any>;
  pipeline: string;
  model: string;
  agent: string;
  timeline: TimelineItem[];
  state_machine: StateMachine;
  trace_id: string;
  fallback_used?: string;
  success?: boolean;
  error?: { code: string; message: string };
  clarification_needed?: boolean;
}

export interface TimelineItem {
  agent: string;
  step: string;
  input?: string;
  output?: string;
  timestamp?: number;
}

export interface StateMachine {
  current: string;
  history: string[];
}

// ── UI Schema ────────────────────────────────────────────────

export interface UiSchemaV24 {
  blocks: UiBlock[];
}

export interface UiBlock {
  type: string;
  title?: string | { zh: string; en: string };
  items?: any;
  content?: string;
  rows?: any[];
  data?: any;
  blocks?: UiBlock[];
  states?: Record<string, any>;
  code?: string;
}

// ── OutputCard ───────────────────────────────────────────────

export interface OutputCard {
  id: string;
  type: string;
  title?: { zh: string; en: string };
  content?: { zh: string; en: string };
  rows?: any[];
  code?: string;
  payload: Record<string, any>;
}

// ── API Response ─────────────────────────────────────────────

export interface V24Response {
  execution: ExecutionResultV24;
  ui_schema: UiSchemaV24;
  output: any;
}
