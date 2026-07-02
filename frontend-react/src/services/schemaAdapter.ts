import { OutputCard } from '../state/outputState';

export const schemaAdapter = {
  toOutputCards(schema: any): OutputCard[] {
    if (!schema) return [];

    const cards: OutputCard[] = [];

    const extractBilingual = (obj: any): { zh: string; en: string } => {
      if (typeof obj === 'string') {
        return { zh: obj, en: obj };
      }
      if (obj && typeof obj === 'object') {
        return {
          zh: obj.zh || '',
          en: obj.en || '',
        };
      }
      return { zh: '', en: '' };
    };

    const processNode = (node: any, order = 0) => {
      if (!node || typeof node !== 'object') return;

      // 递归处理 children
      if (Array.isArray(node.children)) {
        node.children.forEach((child: any, index: number) =>
          processNode(child, index)
        );
        return;
      }

      // UI Schema 标准组件
      if (node.component) {
        cards.push({
          cardId: node.cardId || crypto.randomUUID(),
          order: node.order ?? order,

          componentType: node.component,
          props: node.props || {},

          title: node.title ? extractBilingual(node.title) : undefined,
          content: node.content ? extractBilingual(node.content) : undefined,

          collapsed: node.collapsed || false,
          highlighted: node.highlighted || false,
        });
        return;
      }

      // 兼容旧版 card/text 节点
      if (node.type === 'card' || node.type === 'text') {
        cards.push({
          cardId: crypto.randomUUID(),
          order,

          componentType: node.type,
          props: node.props || {},

          title: extractBilingual(node.title),
          content: extractBilingual(node.content),

          collapsed: node.collapsed || false,
          highlighted: node.highlighted || false,
        });
      }
    };

    processNode(schema);
    return cards.sort((a, b) => a.order - b.order);
  }
};
