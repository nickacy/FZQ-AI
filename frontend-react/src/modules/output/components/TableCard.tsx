import React from 'react';

import { useThemeState } from '../../../state/themeState';
import { useLanguageStore } from '../../../state/languageState';
import { useExecutionState } from '../../../state/executionState';
import { useAgentState } from '../../../state/agentState';

import { BilingualText } from '../../../components/i18n/BilingualText';

interface TableCell {
  zh: string;
  en: string;
}

interface TableCardProps {
  headers: TableCell[];
  rows: TableCell[][];
  title?: { zh: string; en: string };
  description?: { zh: string; en: string };
  agentId?: string;
}

export const TableCard: React.FC<TableCardProps> = ({
  headers,
  rows,
  title,
  description,
  agentId,
}) => {
  const { theme } = useThemeState();
  const { current } = useLanguageStore();
  const { isStreaming } = useExecutionState();
  const { agents } = useAgentState();

  const agent = agents.find((a) => a.id === agentId);

  if (!headers || headers.length === 0) {
    return (
      <div
        className="table-card__empty"
        style={{ color: theme.colors.mutedText }}
      >
        <BilingualText zh="暂无表格数据" en="No table data" />
      </div>
    );
  }

  return (
    <div
      className="table-card"
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
        aria-label="Structured Table"
        className="table-card__table"
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          color: theme.colors.text,
        }}
      >
        <thead>
          <tr>
            {headers.map((header, index) => (
              <th
                key={index}
                className="table-card__th"
                style={{
                  borderBottom: `1px solid ${theme.colors.tableBorder}`,
                  padding: '8px',
                  color: theme.colors.tableHeader,
                }}
              >
                <BilingualText zh={header.zh} en={header.en} />
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {rows.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className="table-card__tr"
              style={{
                borderBottom: `1px solid ${theme.colors.tableBorder}`,
              }}
            >
              {row.map((cell, cellIndex) => (
                <td
                  key={cellIndex}
                  className="table-card__td"
                  style={{
                    padding: '8px',
                    verticalAlign: 'top',
                  }}
                >
                  <BilingualText zh={cell.zh} en={cell.en} />
                </td>
              ))}
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
