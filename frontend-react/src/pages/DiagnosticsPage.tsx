import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";

export default function DiagnosticsPage() {
  return (
    <div>
      <SectionTitle title="Diagnostics" />

      <Panel>
        <p>System diagnostics will appear here.</p>
      </Panel>
    </div>
  );
}
