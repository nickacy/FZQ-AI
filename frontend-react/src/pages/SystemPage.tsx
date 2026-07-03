import { Card } from "../components/ui/Card";
import { SectionTitle } from "../components/ui/SectionTitle";

export default function SystemPage() {
  return (
    <div>
      <SectionTitle title="System Info" />

      <Card>
        <p>System version, health, and status will appear here.</p>
      </Card>
    </div>
  );
}
