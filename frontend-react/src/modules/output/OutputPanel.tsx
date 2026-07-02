import React from 'react';

import { useThemeState } from '../../state/themeState';
import { useExecutionState } from '../../state/executionState';
import { useOutputState } from '../../state/outputState';

import { BilingualText } from '../../components/i18n/BilingualText';

// --- Component Registry ---
import { OutputCard } from './OutputCard';
import { RiskRadar } from './components/RiskRadar';
import { PolicyMatrix } from './components/PolicyMatrix';
import { OpinionGraph } from './components/OpinionGraph';
import { TableCard } from './components/TableCard';
import { MultiAgentOutput } from './components/MultiAgentOutput';

const componentRegistry: Record<string, React.FC<any>> = {
  TextCard: OutputCard,
  Card: OutputCard,
  RiskRadar,
  PolicyMatrix,
  OpinionGraph,
  TableCard,
  MultiAgentOutput,
};

export const OutputPanel: React.FC = () => {
  const { theme } = useThemeState();
  const { isStreaming } = useExecutionState();
  const { cards } = useOutputState();

  if (cards.length === 0) {
    return (
      <div
        className="output-panel__empty"
        style={{ color: theme.colors.mutedText }}
      >
        <BilingualText zh="暂无输出结果" en="No output available" />
      </div>
    );
  }

  return (
    <div
      className="output-panel"
      style={{
        backgroundColor: theme.colors.panelBackground,
        border: `1px solid ${theme.colors.panelBorder}`,
        padding: '16px',
        borderRadius: '8px',
      }}
    >
      {/* --- Header --- */}
      <h3
        style={{
          marginBottom: '12px',
          color: theme.colors.text,
        }}
      >
        <BilingualText zh="输出结果" en="Output Results" />
      </h3>

      {/* --- Cards --- */}
      {cards
        .sort((a, b) => a.order - b.order)
        .map((card) => {
          const Component = componentRegistry[card.componentType] || OutputCard;

          return (
            <div key={card.cardId} style={{ marginBottom: '16px' }}>
              <Component {...card} />
            </div>
          );
        })}

      {/* --- Streaming Indicator --- */}
      {isStreaming && (
        <div
          className="output-panel__streaming"
          style={{
            marginTop: '12px',
            color: theme.colors.accent,
            fontSize: '12px',
            textAlign: 'center',
          }}
        >
          <BilingualText zh="流式生成中..." en="Streaming..." />
        </div>
      )}
    </div>
  );
};
