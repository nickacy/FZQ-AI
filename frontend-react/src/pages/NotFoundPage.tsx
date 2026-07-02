import React from 'react';
import { BilingualText } from '../../components/i18n/BilingualText';

export const NotFoundPage: React.FC = () => {
  return (
    <div style={{ padding: '24px', textAlign: 'center' }}>
      <h1>404</h1>
      <p><BilingualText zh="页面未找到" en="Page Not Found" /></p>
    </div>
  );
};
