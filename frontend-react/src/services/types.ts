/**
 * V24 Contract Types
 * Must match backend DTOs exactly.
 */

// ── Error ────────────────────────────────────────────────────

export interface ApiError {
  code: string;
  message: string;
}

// ── Execution ────────────────────────────────────────────────

export interface ExecutionResultV24 {
  intent: Record<string, unknown>;
  route: Record<string, unknown>;
  pipeline: string;
  model: string;
  agent: string;
  timeline: TimelineItem[];
  state_machine: StateMachine;
  trace_id: string;
  fallback_used?: string;
  success?: boolean;
  error?: ApiError;
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
  items?: unknown;
  content?: string;
  rows?: unknown[];
  data?: unknown;
  blocks?: UiBlock[];
  states?: Record<string, unknown>;
  code?: string;
}

// ── OutputCard ─────────────────────────────────────────────────

export interface OutputCard {
  id: string;
  type: string;
  title?: { zh: string; en: string };
  content?: { zh: string; en: string };
  rows?: unknown[];
  code?: string;
  payload: Record<string, unknown>;
}

// ── API Response ───────────────────────────────────────────────

export interface V24Response {
  execution: ExecutionResultV24;
  ui_schema: UiSchemaV24;
  output: unknown;
}
