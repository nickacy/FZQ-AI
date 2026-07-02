import React from 'react';

import { useThemeState } from '../../../state/themeState';
import { useLanguageState } from '../../../state/languageState';
import { useExecutionState } from '../../../state/executionState';
import { useAgentState } from '../../../state/agentState';

import { BilingualText } from '../../../components/i18n/BilingualText';

interface PolicyItem {
  id: string;
  title: { zh: string; en: string };
  impact: { zh: string; en: string };
  keyPoints: { zh: string; en: string }[];
}

interface PolicyMatrixProps {
  policies: PolicyItem[];
  title?: { zh: string; en: string };
  description?: { zh: string; en: string };
  agentId?: string;
}

export const PolicyMatrix: React.FC<PolicyMatrixProps> = ({
  policies,
  title,
  description,
  agentId,
}) => {
  const { theme } = useThemeState();
  const { current } = useLanguageState();
  const { isStreaming } = useExecutionState();
  const { agents } = useAgentState();

  const agent = agents.find((a) => a.id === agentId);

  if (!policies || policies.length === 0) {
    return (
      <div
        className="policy-matrix__empty"
        style={{ color: theme.colors.mutedText }}
      >
        <BilingualText zh="暂无政策数据" en="No policy data" />
      </div>
    );
  }

  return (
    <div
      className="policy-matrix"
      style={{
        backgroundColor: theme.colors.panelBackground,
        border: `1px solid ${theme.colors.panelBorder}`,
        padding: '16px',
        borderRadius: '8px',
      }}
    >
      {/* --- Title --- */}
      {title && (
        <h4 style={{ color: theme.colors.text, marginBottom: '6px' }}>
          <BilingualText zh={title.zh} en={title.en} />
        </h4>
      )}

      {/* --- Description --- */}
      {description && (
        <p
          style={{
            color: theme.colors.mutedText,
            marginBottom: '12px',
            fontSize: '12px',
          }}
        >
          <BilingualText zh={description.zh} en={description.en} />
        </p>
      )}

      {/* --- Agent Info --- */}
      {agent && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            marginBottom: '12px',
            color: agent.color,
          }}
        >
          <div
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: agent.color,
            }}
          />
          <BilingualText zh={agent.name.zh} en={agent.name.en} />
        </div>
      )}

      {/* --- Table --- */}
      <table
        role="table"
        aria-label="Policy Matrix"
        className="policy-matrix__table"
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          color: theme.colors.text,
        }}
      >
        <thead>
          <tr>
            <th
              style={{
                borderBottom: `1px solid ${theme.colors.tableBorder}`,
                padding: '8px',
                color: theme.colors.tableHeader,
              }}
            >
              <BilingualText zh="政策标题" en="Policy Title" />
            </th>
            <th
              style={{
                borderBottom: `1px solid ${theme.colors.tableBorder}`,
                padding: '8px',
                color: theme.colors.tableHeader,
              }}
            >
              <BilingualText zh="影响分析" en="Impact Analysis" />
            </th>
            <th
              style={{
                borderBottom: `1px solid ${theme.colors.tableBorder}`,
                padding: '8px',
                color: theme.colors.tableHeader,
              }}
            >
              <BilingualText zh="关键要点" en="Key Points" />
            </th>
          </tr>
        </thead>

        <tbody>
          {policies.map((policy) => (
            <tr
              key={policy.id}
              className="policy-matrix__row"
              style={{
                borderBottom: `1px solid ${theme.colors.tableBorder}`,
              }}
            >
              <td
                className="policy-matrix__cell"
                style={{ padding: '8px', verticalAlign: 'top' }}
              >
                <BilingualText zh={policy.title.zh} en={policy.title.en} />
              </td>

              <td
                className="policy-matrix__cell"
                style={{ padding: '8px', verticalAlign: 'top' }}
              >
                <BilingualText zh={policy.impact.zh} en={policy.impact.en} />
              </td>

              <td
                className="policy-matrix__cell"
                style={{ padding: '8px', verticalAlign: 'top' }}
              >
                <ul style={{ margin: 0, paddingLeft: '16px' }}>
                  {policy.keyPoints.map((point, index) => (
                    <li key={index} style={{ marginBottom: '4px' }}>
                      <BilingualText zh={point.zh} en={point.en} />
                    </li>
                  ))}
                </ul>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* --- Streaming Indicator --- */}
      {isStreaming && (
        <div
          style={{
            marginTop: '8px',
            color: theme.colors.accent,
            fontSize: '12px',
            textAlign: 'center',
          }}
        >
          <BilingualText zh="流式更新中..." en="Streaming..." />
        </div>
      )}
    </div>
  );
};
