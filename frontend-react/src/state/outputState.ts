import { create } from 'zustand';

export interface OutputCard {
  cardId: string;
  order: number;

  componentType: string;               // 来自 UI Schema
  props: Record<string, any>;          // 来自 UI Schema
  type?: string;                       // UI block type
  rows?: any[];                        // Table row data
  code?: string;                       // Code block content

  title?: { zh: string; en: string };
  content?: { zh: string; en: string };

  collapsed: boolean;
  highlighted: boolean;
}

interface OutputState {
  cards: OutputCard[];
  uiSchema: Record<string, any>;
  timeline: any[];
  stateMachine: { current: string; history: string[] };
  traceId: string;

  // Actions
  setCards: (cards: OutputCard[]) => void;
  toggleCollapse: (cardId: string) => void;
  highlightCard: (cardId: string, value: boolean) => void;

  resetOutputs: () => void;
}

export const useOutputState = create<OutputState>((set) => ({
  cards: [],
  uiSchema: {},
  timeline: [],
  stateMachine: { current: "INIT", history: [] },
  traceId: "",

  setCards: (cards) => set({ cards }),

  toggleCollapse: (cardId) =>
    set((state) => ({
      cards: state.cards.map((card) =>
        card.cardId === cardId
          ? { ...card, collapsed: !card.collapsed }
          : card
      ),
    })),

  highlightCard: (cardId, value) =>
    set((state) => ({
      cards: state.cards.map((card) =>
        card.cardId === cardId ? { ...card, highlighted: value } : card
      ),
    })),

  resetOutputs: () =>
    set({
      cards: [],
  uiSchema: {},
  timeline: [],
  stateMachine: { current: "INIT", history: [] },
  traceId: "",
    }),
}));
