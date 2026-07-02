import React from 'react';
import { Phase } from '../../state/executionState';

import { useThemeState } from '../../state/themeState';
import { useExecutionState } from '../../state/executionState';
import { useAgentState } from '../../state/agentState';

import { BilingualText } from '../../components/i18n/BilingualText';

const phases: Phase[] = ['DECOMPOSE', 'ROUTE', 'ACT', 'REFLECT', 'FINALIZE'];

const phaseLabels: Record<Phase, { zh: string; en: string }> = {
  DECOMPOSE: { zh: '分解任务', en: 'Decompose' },
  ROUTE: { zh: '路由分配', en: 'Route' },
  ACT: { zh: '智能体执行', en: 'Act' },
  REFLECT: { zh: '反思纠错', en: 'Reflect' },
  FINALIZE: { zh: '输出结果', en: 'Finalize' },
};

const phaseDescriptions: Record<Phase, { zh: string; en: string }> = {
  DECOMPOSE: { zh: '分析用户意图并拆解任务', en: 'Analyze intent and break down the task' },
  ROUTE: { zh: '选择最佳智能体或管线', en: 'Select best agent or pipeline' },
  ACT: { zh: '智能体执行推理或行动', en: 'Agent performs reasoning or action' },
  REFLECT: { zh: '自我反思并纠错', en: 'Self‑critique and correction' },
  FINALIZE: { zh: '生成最终结构化输出', en: 'Produce final structured output' },
};

export const ExecutionPanel: React.FC = () => {
  const { theme } = useThemeState();
  const { currentPhase, stateHistory, isStreaming } = useExecutionState();
  const { currentAgent, agents } = useAgentState();

  const currentIndex = phases.indexOf(currentPhase);
  const activeAgent = agents.find((a) => a.id === currentAgent);

  return (
    <div
      className="execution-panel"
      style={{
        backgroundColor: theme.colors.panelBackground,
        border: `1px solid ${theme.colors.panelBorder}`,
        padding: '16px',
        borderRadius: '8px',
      }}
    >
      {/* --- Agent Info --- */}
      {activeAgent && (
        <div className="execution-panel__agent-info" style={{ marginBottom: '12px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: activeAgent.color || theme.colors.text,
            }}
          >
            <div
              style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: activeAgent.color || theme.colors.accent,
              }}
            />
            <BilingualText zh={activeAgent.name.zh} en={activeAgent.name.en} />
          </div>
        </div>
      )}

      {/* --- Phase Nodes --- */}
      <div className="execution-panel__nodes">
        {phases.map((phase, index) => {
          const isCompleted = index < currentIndex;
          const isActive = index === currentIndex;

          return (
            <React.Fragment key={phase}>
              {index > 0 && (
                <div
                  className="execution-panel__connector"
                  style={{
                    height: '2px',
                    flex: 1,
                    backgroundColor: isCompleted
                      ? theme.colors.phaseCompleted
                      : theme.colors.phasePending,
                    transition: 'background-color 0.3s ease',
                  }}
                />
              )}

              <div
                className="execution-panel__node"
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <div
                  className="execution-panel__circle"
                  style={{
                    width: '18px',
                    height: '18px',
                    borderRadius: '50%',
                    backgroundColor: isActive
                      ? theme.colors.phaseActive
                      : isCompleted
                      ? theme.colors.phaseCompleted
                      : theme.colors.phasePending,
                    boxShadow: isActive
                      ? `0 0 8px ${theme.colors.phaseActive}`
                      : 'none',
                    transition: 'all 0.3s ease',
                  }}
                />

                <div
                  className="execution-panel__label"
                  style={{ textAlign: 'center', fontSize: '12px' }}
                >
                  <BilingualText zh={phaseLabels[phase].zh} en={phaseLabels[phase].en} />
                </div>

                <div
                  className="execution-panel__description"
                  style={{
                    textAlign: 'center',
                    fontSize: '10px',
                    color: theme.colors.mutedText,
                    maxWidth: '120px',
                  }}
                >
                  <BilingualText
                    zh={phaseDescriptions[phase].zh}
                    en={phaseDescriptions[phase].en}
                  />
                </div>
              </div>
            </React.Fragment>
          );
        })}
      </div>

      {/* --- Streaming Indicator --- */}
      {isStreaming && (
        <div
          className="execution-panel__streaming"
          style={{
            marginTop: '12px',
            color: theme.colors.accent,
            fontSize: '12px',
            textAlign: 'center',
          }}
        >
          <BilingualText zh="流式执行中..." en="Streaming..." />
        </div>
      )}
    </div>
  );
};
