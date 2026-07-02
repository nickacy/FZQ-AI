import React from 'react';

import { useWorkspaceState } from '../state/workspaceState';
import { useExecutionState } from '../state/executionState';
import { useAgentState } from '../state/agentState';
import { useOutputState } from '../state/outputState';
import { useSystemState } from '../state/systemState';
import { useThemeState } from '../state/themeState';

import { entryService } from '../services/entryService';
import { schemaAdapter } from '../services/schemaAdapter';

import { BilingualText } from '../components/i18n/BilingualText';
import { InputPanel } from '../modules/workspace/InputPanel';
import { ExecutionPanel } from '../modules/execution/ExecutionPanel';
import { TimelinePanel } from '../modules/execution/TimelinePanel';
import { OutputPanel } from '../modules/output/OutputPanel';

export const WorkspacePage: React.FC = () => {
  const {
    inputText,
    setInputText,
    resetWorkspace,
    isRunning,
    setRunning,
  } = useWorkspaceState();

  const { currentPhase, timeline, uiSchema } = useExecutionState();
  const { currentAgent } = useAgentState();
  const { setCards, resetOutputs } = useOutputState();
  const { setApiStatus, setSystemHealth } = useSystemState();
  const { theme } = useThemeState();

  const handleExecute = async () => {
    if (!inputText.trim()) return;

    // --- 清空旧状态 ---
    resetWorkspace();
    resetOutputs();
    setRunning(true);

    try {
      const data = await entryService.runEntry(inputText);

      if (data.ui_schema) {
        const cards = schemaAdapter.toOutputCards(data.ui_schema);
        setCards(cards);
      }

      setApiStatus('connected');
      setSystemHealth('healthy');
    } catch (error: any) {
      setApiStatus('error');
      setSystemHealth('degraded');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div
      className="workspace-page"
      style={{
        backgroundColor: theme.colors.background,
        color: theme.colors.text,
      }}
    >
      {/* --- Input Section --- */}
      <div className="workspace-page__input-section">
        <InputPanel
          value={inputText}
          onChange={setInputText}
          onSubmit={handleExecute}
          isLoading={isRunning}
        />
      </div>

      {/* --- Execution Section --- */}
      <div className="workspace-page__execution-section">
        <div className="workspace-page__state-machine">
          <h3>
            <BilingualText zh="执行状态" en="Execution State" />
          </h3>
          <ExecutionPanel currentPhase={currentPhase} />
        </div>

        <div className="workspace-page__timeline">
          <h3>
            <BilingualText zh="协作链路" en="Collaboration Timeline" />
          </h3>
          <TimelinePanel timeline={timeline} />
        </div>
      </div>

      {/* --- Output Section --- */}
      <div className="workspace-page__output-section">
        <OutputPanel uiSchema={uiSchema} />
      </div>
    </div>
  );
};
