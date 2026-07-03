import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";

export default function DebugPage() {
  return (
    <div>
      <SectionTitle title="Debug Tools" />

      <Panel>
        <p>Debug information will appear here.</p>
      </Panel>
    </div>
  );
}
