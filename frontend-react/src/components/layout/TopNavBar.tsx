import React from 'react';

import { useLanguageStore } from '../../state/languageState';
import { useThemeState } from '../../state/themeState';
import { useSystemState } from '../../state/systemState';

import { BilingualText } from '../i18n/BilingualText';

export const TopNavBar: React.FC = () => {
  const { current, setLanguage } = useLanguageStore();
  const { current: themeMode, toggleTheme, theme } = useThemeState();
  const { apiStatus, networkStatus } = useSystemState();

  const isDark = themeMode === 'dark';

  return (
    <header
      className="top-nav-bar"
      style={{
        backgroundColor: theme.colors.navBackground,
        color: theme.colors.navText,
        borderBottom: `1px solid ${theme.colors.navBorder}`,
      }}
    >
      {/* --- Brand --- */}
      <div className="top-nav-bar__brand">
        <h1>
          <BilingualText zh="FZQ-AI 智能体系统" en="FZQ-AI Intelligence System" />
        </h1>
      </div>

      {/* --- Actions --- */}
      <div className="top-nav-bar__actions">
        {/* Theme Toggle */}
        <button onClick={toggleTheme} className="top-nav-bar__btn">
          <BilingualText
            zh={isDark ? '浅色模式' : '深色模式'}
            en={isDark ? 'Light Mode' : 'Dark Mode'}
          />
        </button>

        {/* Language Toggle */}
        <button
          onClick={() => setLanguage(current === 'zh' ? 'en' : 'zh')}
          className="top-nav-bar__btn"
        >
          <BilingualText zh="English" en="中文" />
        </button>

        {/* System Status */}
        <div className="top-nav-bar__status">
          <span
            style={{
              color:
                apiStatus === 'connected'
                  ? theme.colors.statusOk
                  : theme.colors.statusError,
            }}
          >
            <BilingualText
              zh={apiStatus === 'connected' ? '后端已连接' : '后端错误'}
              en={apiStatus === 'connected' ? 'Backend Connected' : 'Backend Error'}
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
      </div>
    </header>
  );
};
