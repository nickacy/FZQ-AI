import React, { Component, ErrorInfo, ReactNode } from 'react';

import { useSystemState } from '../../state/systemState';
import { useThemeState } from '../../state/themeState';
import { BilingualText } from '../i18n/BilingualText';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);

    // --- 更新系统状态 ---
    const { setSystemHealth, setApiStatus } = useSystemState.getState();
    setSystemHealth('degraded');
    setApiStatus('error');

    // --- 预留错误上报接口 ---
    // reportError(error, errorInfo);
  }

  private resetError = () => {
    this.setState({ hasError: false, error: null });

    const { setSystemHealth, setApiStatus } = useSystemState.getState();
    setSystemHealth('healthy');
    setApiStatus('connected');
  };

  public render() {
    if (this.state.hasError) {
      const { theme } = useThemeState.getState();

      return (
        <div
          className="error-boundary"
          style={{
            backgroundColor: theme.colors.errorBackground,
            color: theme.colors.errorText,
            padding: '24px',
            borderRadius: '8px',
            margin: '16px',
          }}
        >
          <h2>
            <BilingualText zh="系统发生错误" en="System Error" />
          </h2>

          <p>{this.state.error?.message}</p>

          <button
            onClick={this.resetError}
            style={{
              marginTop: '16px',
              padding: '8px 16px',
              backgroundColor: theme.colors.buttonPrimary,
              color: theme.colors.buttonText,
              borderRadius: '6px',
              border: 'none',
            }}
          >
            <BilingualText zh="返回工作台" en="Return to Workspace" />
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
