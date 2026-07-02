import React from 'react';
import { BilingualText } from '../../components/i18n/BilingualText';

export const DiagnosticsPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <h1><BilingualText zh="诊断" en="Diagnostics" /></h1>
      <p><BilingualText zh="系统诊断页面" en="System Diagnostics" /></p>
    </div>
  );
};
