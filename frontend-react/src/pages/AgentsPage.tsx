import { Card } from "../components/ui/Card";
import { SectionTitle } from "../components/ui/SectionTitle";
import { Button } from "../components/ui/Button";
import { t } from "../i18n";
import { useLanguageStore } from "../state/languageState";

export default function AgentsPage() {
  const lang = useLanguageStore((s) => s.language);

  return (
    <div>
      <SectionTitle title={t("nav.agents", lang)} />

      <Card>
        <h3>Agent List</h3>
        <p>All configured agents will appear here.</p>
        <Button variant="primary">Add Agent</Button>
      </Card>
    </div>
  );
}
