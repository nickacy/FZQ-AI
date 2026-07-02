import React from 'react';
import { BilingualText } from '../../components/i18n/BilingualText';

export const AgentsPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <h1><BilingualText zh="智能体" en="Agents" /></h1>
      <p><BilingualText zh="智能体管理页面" en="Agent Management" /></p>
    </div>
  );
};
