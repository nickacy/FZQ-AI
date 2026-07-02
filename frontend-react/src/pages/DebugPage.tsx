import React from 'react';
import { BilingualText } from '../../components/i18n/BilingualText';

export const DebugPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <h1><BilingualText zh="调试" en="Debug" /></h1>
      <p><BilingualText zh="调试工具页面" en="Debug Tools" /></p>
    </div>
  );
};
