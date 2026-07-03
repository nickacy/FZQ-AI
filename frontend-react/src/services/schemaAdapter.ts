import { useLanguageStore } from "../state/languageState";

interface RawCard {
  type: string;
  title?: { zh: string; en: string } | string;
  content?: { zh: string; en: string } | string;
  rows?: any[];
  code?: string;
}

interface OutputCard {
  type: string;
  title?: { zh: string; en: string };
  content?: { zh: string; en: string };
  rows?: any[];
  code?: string;
}

export const schemaAdapter = {
  toOutputCards(uiSchema: any): OutputCard[] {
    if (!uiSchema || !Array.isArray(uiSchema.cards)) return [];

    return uiSchema.cards.map((raw: RawCard) => {
      const card: OutputCard = {
        type: raw.type,
        rows: raw.rows,
        code: raw.code,
        title: normalizeBilingual(raw.title),
        content: normalizeBilingual(raw.content),
      };

      return card;
    });
  }
};

/**
 * 将 title/content 转换为双语结构
 * 支持三种情况：
 * 1. { zh: "...", en: "..." }
 * 2. "纯字符串" → 自动转换为 { zh: str, en: str }
 * 3. undefined → 返回 { zh: "", en: "" }
 */
function normalizeBilingual(value: any): { zh: string; en: string } {
  if (!value) {
    return { zh: "", en: "" };
  }

  if (typeof value === "string") {
    return { zh: value, en: value };
  }

  if (typeof value === "object" && value.zh && value.en) {
    return value;
  }

  // fallback：如果结构不完整，自动补齐
  return {
    zh: value.zh ?? "",
    en: value.en ?? ""
  };
}
