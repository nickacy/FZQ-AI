import React, { useState } from 'react';

import { TimelineEvent } from '../../state/executionState';
import { useThemeState } from '../../state/themeState';
import { useExecutionState } from '../../state/executionState';
import { useAgentState } from '../../state/agentState';

import { BilingualText } from '../../components/i18n/BilingualText';

interface TimelinePanelProps {
  timeline: TimelineEvent[];
}

export const TimelinePanel: React.FC<TimelinePanelProps> = ({ timeline }) => {
  const { theme } = useThemeState();
  const { isStreaming } = useExecutionState();
  const { agents } = useAgentState();

  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  const toggle = (index: number) =>
    setExpanded((prev) => ({ ...prev, [index]: !prev[index] }));

  if (timeline.length === 0) {
    return (
      <div
        className="timeline-panel__empty"
        style={{ color: theme.colors.mutedText }}
      >
        <BilingualText zh="暂无协作链路数据" en="No timeline data available" />
      </div>
    );
  }

  return (
    <div
      className="timeline-panel"
      style={{
        backgroundColor: theme.colors.panelBackground,
        border: `1px solid ${theme.colors.panelBorder}`,
        padding: '16px',
        borderRadius: '8px',
      }}
    >
      {timeline.map((event, index) => {
        const agent = agents.find((a) => a.id === event.agent);

        return (
          <div
            key={index}
            className="timeline-panel__event"
            style={{
              marginBottom: '16px',
              paddingBottom: '12px',
              borderBottom: `1px solid ${theme.colors.panelBorder}`,
            }}
          >
            {/* --- Header --- */}
            <div
              className="timeline-panel__header"
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '6px',
              }}
            >
              <span
                className="timeline-panel__timestamp"
                style={{ color: theme.colors.mutedText }}
              >
                {new Date(event.timestamp).toLocaleTimeString()}
              </span>

              <span
                className="timeline-panel__agent"
                style={{
                  color: agent?.color || theme.colors.accent,
                  fontWeight: 600,
                }}
              >
                <BilingualText zh="智能体" en="Agent" />: {agent?.name.zh || event.agent}
              </span>
            </div>

            {/* --- Step --- */}
            <div
              className="timeline-panel__step"
              style={{
                fontWeight: 600,
                marginBottom: '8px',
                color: theme.colors.text,
              }}
            >
              {event.step}
            </div>

            {/* --- Expand/Collapse --- */}
            <button
              onClick={() => toggle(index)}
              style={{
                background: 'none',
                border: 'none',
                color: theme.colors.accent,
                cursor: 'pointer',
                marginBottom: '8px',
              }}
            >
              {expanded[index] ? (
                <BilingualText zh="收起详情" en="Hide Details" />
              ) : (
                <BilingualText zh="展开详情" en="Show Details" />
              )}
            </button>

            {/* --- Details --- */}
            {expanded[index] && (
              <div
                className="timeline-panel__details"
                style={{
                  backgroundColor: theme.colors.detailBackground,
                  padding: '12px',
                  borderRadius: '6px',
                }}
              >
                <div className="timeline-panel__detail">
                  <strong>
                    <BilingualText zh="输入:" en="Input:" />
                  </strong>{' '}
                  {event.input}
                </div>

                <div className="timeline-panel__detail" style={{ marginTop: '6px' }}>
                  <strong>
                    <BilingualText zh="输出:" en="Output:" />
                  </strong>{' '}
                  {event.output}
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* --- Streaming Indicator --- */}
      {isStreaming && (
        <div
          className="timeline-panel__streaming"
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
