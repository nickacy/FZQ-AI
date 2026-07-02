import React, { useEffect } from 'react';

import { AppRoutes } from './routes';
import { TopNavBar } from '../components/layout/TopNavBar';
import { BottomNavBar } from '../components/layout/BottomNavBar';

import { useSystemState } from '../state/systemState';
import { useThemeState } from '../state/themeState';
import { useLanguageState } from '../state/languageState';

import { ErrorBoundary } from '../components/layout/ErrorBoundary';

export const AppShell: React.FC = () => {
  const { setNetworkStatus, setApiStatus, setBackendVersion, setHeartbeat } =
    useSystemState();

  const { theme } = useThemeState();
  const { current } = useLanguageState();

  // --- 网络状态监听 ---
  useEffect(() => {
    const handleOnline = () => setNetworkStatus('online');
    const handleOffline = () => setNetworkStatus('offline');

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // --- 后端心跳轮询（使用 /health 端点） ---
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('/health');
        if (res.ok) {
          const data = await res.json();
          setApiStatus('connected');
          setBackendVersion(data.version || '');
          setHeartbeat(Date.now());
        } else {
          setApiStatus('error');
        }
      } catch {
        setApiStatus('error');
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className="app-shell"
      style={{
        backgroundColor: theme.colors.background,
        color: theme.colors.text,
      }}
    >
      <TopNavBar />

      <main className="app-main-content">
        <ErrorBoundary>
          <AppRoutes />
        </ErrorBoundary>
      </main>

      <BottomNavBar />
    </div>
  );
};
