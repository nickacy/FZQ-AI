import React from 'react';
import { BilingualText } from '../../components/i18n/BilingualText';

export const HistoryPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <h1><BilingualText zh="历史记录" en="History" /></h1>
      <p><BilingualText zh="暂无历史记录" en="No history yet" /></p>
    </div>
  );
};
