import React from 'react';
import { BilingualText } from '../../components/i18n/BilingualText';

export const SettingsPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <h1><BilingualText zh="设置" en="Settings" /></h1>
      <p><BilingualText zh="系统设置页面" en="System Settings" /></p>
    </div>
  );
};
