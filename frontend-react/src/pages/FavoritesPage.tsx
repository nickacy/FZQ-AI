import React from 'react';
import { BilingualText } from '../../components/i18n/BilingualText';

export const FavoritesPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <h1><BilingualText zh="收藏" en="Favorites" /></h1>
      <p><BilingualText zh="暂无收藏" en="No favorites yet" /></p>
    </div>
  );
};
