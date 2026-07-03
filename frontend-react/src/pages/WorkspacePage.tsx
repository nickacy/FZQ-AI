import { Card } from "../components/ui/Card";
import { Panel } from "../components/ui/Panel";
import { SectionTitle } from "../components/ui/SectionTitle";
import { Button } from "../components/ui/Button";
import { t } from "../i18n";
import { useLanguageStore } from "../state/languageState";

export default function WorkspacePage() {
  const lang = useLanguageStore((s) => s.language);

  return (
    <div>
      <SectionTitle title={t("nav.workspace", lang)} />

      <Panel>
        <h3>{t("execution.running", lang)}</h3>
        <p>Pipeline execution details will appear here.</p>
        <Button variant="primary">Run Pipeline</Button>
      </Panel>

      <Card>
        <h4>{t("output.policyMatrix", lang)}</h4>
        <p>Policy matrix visualization will appear here.</p>
      </Card>
    </div>
  );
}
