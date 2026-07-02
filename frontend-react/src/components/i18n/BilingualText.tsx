import React from 'react';

interface Props {
  zh: string;
  en: string;
}

export const BilingualText: React.FC<Props> = ({ zh, en }) => {
  // 简单实现：根据当前语言显示，但这里不做复杂逻辑
  // 实际应由 useLanguageState 驱动
  return <span>{zh}</span>;
};
