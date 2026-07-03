import React from 'react';
import { BilingualText } from '../../components/i18n/BilingualText';

import { useThemeState } from '../../state/themeState';
import { useLanguageStore } from '../../state/languageState';
import { useWorkspaceState } from '../../state/workspaceState';

interface InputPanelProps {
  value: string;
  onChange: (val: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

export const InputPanel: React.FC<InputPanelProps> = ({
  value,
  onChange,
  onSubmit,
  isLoading,
}) => {
  const { theme } = useThemeState();
  const { current } = useLanguageStore();
  const { smartSuggestions, quickTemplates, inputMode } = useWorkspaceState();

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && value.trim()) {
        onSubmit();
      }
    }
  };

  return (
    <div
      className="input-panel"
      style={{
        backgroundColor: theme.colors.panelBackground,
        color: theme.colors.text,
        border: `1px solid ${theme.colors.panelBorder}`,
        padding: '16px',
        borderRadius: '8px',
      }}
    >
      {/* --- Quick Templates --- */}
      {quickTemplates.length > 0 && (
        <div className="input-panel__templates">
          {quickTemplates.map((tpl) => (
            <button
              key={tpl.id}
              className="input-panel__template-pill"
              onClick={() => onChange(tpl.prompt)}
              style={{
                backgroundColor: theme.colors.templatePill,
                color: theme.colors.templateText,
              }}
            >
              <BilingualText zh={tpl.title.zh} en={tpl.title.en} />
            </button>
          ))}
        </div>
      )}

      {/* --- Textarea --- */}
      <textarea
        className="input-panel__textarea"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={4}
        disabled={isLoading}
        style={{
          backgroundColor: theme.colors.inputBackground,
          color: theme.colors.inputText,
          border: `1px solid ${theme.colors.inputBorder}`,
        }}
      />

      {/* --- Placeholder --- */}
      {!value && (
        <div className="input-panel__placeholder">
          <BilingualText
            zh="请输入你的问题..."
            en="Enter your query..."
          />
        </div>
      )}

      {/* --- Smart Suggestions --- */}
      {smartSuggestions.length > 0 && (
        <div className="input-panel__suggestions">
          {smartSuggestions.map((sug) => (
            <button
              key={sug.id}
              className="input-panel__suggestion"
              onClick={() => onChange(sug.zh)}
              style={{
                backgroundColor: theme.colors.suggestionBackground,
                color: theme.colors.suggestionText,
              }}
            >
              <BilingualText zh={sug.zh} en={sug.en} />
            </button>
          ))}
        </div>
      )}

      {/* --- Character Counter --- */}
      <div
        className="input-panel__counter"
        style={{ color: theme.colors.mutedText }}
      >
        {value.length} / 2000
      </div>

      {/* --- Submit Button --- */}
      <div className="input-panel__actions">
        <button
          className="input-panel__submit-btn"
          onClick={onSubmit}
          disabled={isLoading || !value.trim()}
          style={{
            backgroundColor: theme.colors.buttonPrimary,
            color: theme.colors.buttonText,
            opacity: isLoading ? 0.7 : 1,
          }}
        >
          <BilingualText
            zh={isLoading ? '执行中...' : '提交'}
            en={isLoading ? 'Executing...' : 'Submit'}
          />
        </button>
      </div>
    </div>
  );
};
