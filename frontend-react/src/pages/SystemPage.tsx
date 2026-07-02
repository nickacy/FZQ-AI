import React from 'react';
import { BilingualText } from '../../components/i18n/BilingualText';

export const SystemPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <h1><BilingualText zh="系统" en="System" /></h1>
      <p><BilingualText zh="系统状态监控" en="System Status Monitor" /></p>
    </div>
  );
};
