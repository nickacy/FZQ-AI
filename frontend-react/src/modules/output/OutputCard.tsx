import React from 'react';

import { useThemeState } from '../../state/themeState';
import { useOutputState } from '../../state/outputState';
import { BilingualText } from '../../components/i18n/BilingualText';

interface OutputCardProps {
  cardId: string;
  title?: { zh: string; en: string };
  content?: { zh: string; en: string };
  componentType: string;
  props: Record<string, any>;
  collapsed: boolean;
  highlighted: boolean;
}

export const OutputCard: React.FC<OutputCardProps> = ({
  cardId,
  title,
  content,
  componentType,
  props,
  collapsed,
  highlighted,
}) => {
  const { theme } = useThemeState();
  const { toggleCollapse } = useOutputState();

  const iconMap: Record<string, string> = {
    TextCard: '📝',
    Card: '📝',
    RiskRadar: '📊',
    PolicyMatrix: '📋',
    OpinionGraph: '📈',
    TableCard: '📑',
    MultiAgentOutput: '🤖',
  };

  const icon = iconMap[componentType] || '📄';

  return (
    <div
      className="output-card"
      style={{
        backgroundColor: highlighted
          ? theme.colors.cardHighlight
          : theme.colors.cardBackground,
        border: `1px solid ${theme.colors.cardBorder}`,
        padding: '16px',
        borderRadius: '8px',
        transition: 'background-color 0.3s ease',
      }}
    >
      {/* --- Header --- */}
      <div
        className="output-card__header"
        onClick={() => toggleCollapse(cardId)}
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          cursor: 'pointer',
          marginBottom: '8px',
        }}
      >
        <h4
          className="output-card__title"
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          <span>{icon}</span>
          {title && <BilingualText zh={title.zh} en={title.en} />}
        </h4>

        <span
          className="output-card__toggle"
          style={{ color: theme.colors.accent }}
        >
          <BilingualText
            zh={collapsed ? '展开' : '收起'}
            en={collapsed ? 'Expand' : 'Collapse'}
          />
        </span>
      </div>

      {/* --- Content --- */}
      {!collapsed && (
        <div
          className="output-card__content"
          style={{
            marginTop: '8px',
            color: theme.colors.text,
            lineHeight: 1.6,
          }}
        >
          {/* Text content */}
          {content && (
            <div style={{ marginBottom: '12px' }}>
              <BilingualText zh={content.zh} en={content.en} />
            </div>
          )}

          {/* Structured props */}
          {props && (
            <pre
              style={{
                backgroundColor: theme.colors.detailBackground,
                padding: '12px',
                borderRadius: '6px',
                overflowX: 'auto',
                fontSize: '12px',
              }}
            >
              {JSON.stringify(props, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
};
