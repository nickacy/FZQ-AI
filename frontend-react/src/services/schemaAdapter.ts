/**
 * schemaAdapter.ts — V24-Final
 * Maps backend V24 ui_schema → renderable OutputCard[]
 * Supports all V24 block types: card, text, table, chart, timeline, state_machine
 */

// ── Types ────────────────────────────────────────────────────

export interface OutputCard {
  id: string;
  type: string;
  title?: { zh: string; en: string };
  content?: { zh: string; en: string };
  rows?: any[];
  code?: string;
  payload: Record<string, any>;
}

interface RawBlock {
  type: string;
  title?: string | { zh: string; en: string };
  content?: string;
  items?: any;
  rows?: any[];
  data?: any;
  blocks?: RawBlock[];
  code?: string;
  states?: Record<string, any>;
}

// ── Main Adapter ────────────────────────────────────────────

export function schemaAdapter(uiSchema: any): OutputCard[] {
  if (!uiSchema) return [];

  // Support both { blocks: [...] } (V24) and { cards: [...] } (legacy)
  const blocks: RawBlock[] = uiSchema.blocks ?? uiSchema.cards ?? [];
  if (!Array.isArray(blocks)) return [];

  return blocks.map((block: RawBlock, index: number) => {
    const card: OutputCard = {
      id: `card-${index}-${block.type}`,
      type: block.type,
      title: normalizeBilingual(block.title),
      content: normalizeBilingual(block.content),
      rows: block.rows,
      code: block.code,
      payload: extractPayload(block),
    };
    return card;
  });
}

// ── Payload extraction by card type ──────────────────────────

function extractPayload(block: RawBlock): Record<string, any> {
  switch (block.type) {
    case "card":
      return { items: block.items ?? block };
    case "text":
      return { content: block.content ?? "" };
    case "table":
      return { rows: block.rows ?? [] };
    case "chart":
    case "radar":
    case "line":
      return { data: block.data ?? block };
    case "risk_block":
      return { items: block.items ?? block };
    case "policy_brief_card":
      return { summary: block.items ?? block };
    case "timeline":
      return { items: block.items ?? block.data ?? [] };
    case "state_machine":
      return { states: block.states ?? {} };
    case "layout":
      return { blocks: block.blocks ?? [] };
    default:
      return { raw: block };
  }
}

// ── Helpers ──────────────────────────────────────────────────

function normalizeBilingual(
  value?: string | { zh: string; en: string }
): { zh: string; en: string } {
  if (!value) return { zh: "", en: "" };
  if (typeof value === "string") return { zh: value, en: value };
  return { zh: value.zh ?? "", en: value.en ?? "" };
}

/** Quick check: does uiSchema have renderable content? */
export function hasRenderableCards(uiSchema: any): boolean {
  const cards = schemaAdapter(uiSchema);
  return cards.length > 0;
}
