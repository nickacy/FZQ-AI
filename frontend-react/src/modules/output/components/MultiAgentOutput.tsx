import React, { useState } from 'react';

import { useThemeState } from '../../../state/themeState';
import { useLanguageStore } from '../../../state/languageState';
import { useExecutionState } from '../../../state/executionState';
import { useAgentState } from '../../../state/agentState';

import { BilingualText } from '../../../components/i18n/BilingualText';

export interface AgentOutputBlock {
  agentId: string;
  agentName: { zh: string; en: string };
  status: 'success' | 'error' | 'running';
  resultSummary: { zh: string; en: string };
  details?: { zh: string; en: string };
}

interface MultiAgentOutputProps {
  agents: AgentOutputBlock[];
  title?: { zh: string; en: string };
  description?: { zh: string; en: string };
}

export const MultiAgentOutput: React.FC<MultiAgentOutputProps> = ({
  agents,
  title,
  description,
}) => {
  const { theme } = useThemeState();
  const { current } = useLanguageStore();
  const { isStreaming } = useExecutionState();
  const { agents: agentRegistry } = useAgentState();

  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  if (!agents || agents.length === 0) {
    return (
      <div
        className="multi-agent-output__empty"
        style={{ color: theme.colors.mutedText }}
      >
        <BilingualText zh="暂无多智能体输出" en="No multi-agent output" />
      </div>
    );
  }

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const statusColor = {
    success: theme.colors.success,
    error: theme.colors.error,
    running: theme.colors.running,
  };

  return (
    <div
      className="multi-agent-output"
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

      {/* --- Agent Blocks --- */}
      {agents.map((agent) => {
        const isExpanded = expandedIds.has(agent.agentId);
        const registryAgent = agentRegistry.find((a) => a.id === agent.agentId);

        return (
          <div
            key={agent.agentId}
            role="region"
            aria-label="Agent Output"
            className="multi-agent-output__card"
            style={{
              backgroundColor: theme.colors.cardBackground,
              border: `1px solid ${theme.colors.cardBorder}`,
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '12px',
            }}
          >
            {/* --- Header --- */}
            <div
              className="multi-agent-output__header"
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '8px',
              }}
            >
              <h4
                className="multi-agent-output__name"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  color: registryAgent?.color || theme.colors.text,
                }}
              >
                {/* Agent Avatar */}
                {registryAgent?.avatar && (
                  <img
                    src={registryAgent.avatar}
                    alt="Agent Avatar"
                    style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                    }}
                  />
                )}

                <BilingualText
                  zh={`智能体: ${agent.agentName.zh}`}
                  en={`Agent: ${agent.agentName.en}`}
                />
              </h4>

              {/* Status Badge */}
              <span
                className="multi-agent-output__status"
                style={{
                  color: statusColor[agent.status],
                  fontWeight: 600,
                }}
              >
                <BilingualText
                  zh={
                    agent.status === 'success'
                      ? '成功'
                      : agent.status === 'error'
                      ? '失败'
                      : '执行中'
                  }
                  en={
                    agent.status === 'success'
                      ? 'Success'
                      : agent.status === 'error'
                      ? 'Error'
                      : 'Running'
                  }
                />
              </span>
            </div>

            {/* --- Summary --- */}
            <div
              className="multi-agent-output__summary"
              style={{ marginBottom: '8px', color: theme.colors.text }}
            >
              <BilingualText
                zh={agent.resultSummary.zh}
                en={agent.resultSummary.en}
              />
            </div>

            {/* --- Expand Button --- */}
            {agent.details && (
              <button
                className="multi-agent-output__toggle-btn"
                onClick={() => toggleExpand(agent.agentId)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: theme.colors.accent,
                  cursor: 'pointer',
                  marginBottom: '8px',
                }}
              >
                <BilingualText
                  zh={isExpanded ? '收起详情' : '查看详情'}
                  en={isExpanded ? 'Hide Details' : 'View Details'}
                />
              </button>
            )}

            {/* --- Details --- */}
            {isExpanded && agent.details && (
              <div
                className="multi-agent-output__details"
                style={{
                  backgroundColor: theme.colors.detailBackground,
                  padding: '12px',
                  borderRadius: '6px',
                  color: theme.colors.text,
                }}
              >
                <BilingualText
                  zh={agent.details.zh}
                  en={agent.details.en}
                />
              </div>
            )}
          </div>
        );
      })}

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
