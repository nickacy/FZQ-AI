import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

import { useThemeState } from '../../state/themeState';
import { useLanguageState } from '../../state/languageState';
import { useSystemState } from '../../state/systemState';

import { BilingualText } from '../i18n/BilingualText';

export const BottomNavBar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const { theme } = useThemeState();
  const { current } = useLanguageState();
  const { apiStatus, networkStatus } = useSystemState();

  const navItems = [
    { path: '/workspace', key: 'nav.workspace' },
    { path: '/history', key: 'nav.history' },
    { path: '/favorites', key: 'nav.favorites' },
    { path: '/agents', key: 'nav.agents' },
    { path: '/settings', key: 'nav.settings' },
  ];

  return (
    <nav
      className="bottom-nav-bar"
      style={{
        backgroundColor: theme.colors.navBackground,
        color: theme.colors.navText,
        borderTop: `1px solid ${theme.colors.navBorder}`,
        paddingBottom: 'env(safe-area-inset-bottom)',
      }}
    >
      {/* --- Navigation Items --- */}
      <div className="bottom-nav-bar__items">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;

          return (
            <button
              key={item.path}
              className="bottom-nav-bar__item"
              onClick={() => navigate(item.path)}
              style={{
                color: isActive
                  ? theme.colors.navActive
                  : theme.colors.navText,
              }}
            >
              <BilingualText
                zh={theme.texts.zh[item.key]}
                en={theme.texts.en[item.key]}
              />
            </button>
          );
        })}
      </div>

      {/* --- System Status --- */}
      <div className="bottom-nav-bar__status">
        <span
          style={{
            color:
              apiStatus === 'connected'
                ? theme.colors.statusOk
                : theme.colors.statusError,
          }}
        >
          <BilingualText
            zh={apiStatus === 'connected' ? '后端正常' : '后端错误'}
            en={apiStatus === 'connected' ? 'Backend OK' : 'Backend Error'}
          />
        </span>

        <span
          style={{
            marginLeft: '12px',
            color:
              networkStatus === 'online'
                ? theme.colors.statusOk
                : theme.colors.statusError,
          }}
        >
          <BilingualText
            zh={networkStatus === 'online' ? '在线' : '离线'}
            en={networkStatus === 'online' ? 'Online' : 'Offline'}
          />
        </span>
      </div>
    </nav>
  );
};
