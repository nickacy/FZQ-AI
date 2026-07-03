import { Card } from "../components/ui/Card";
import { SectionTitle } from "../components/ui/SectionTitle";
import { t } from "../i18n";
import { useLanguageStore } from "../state/languageState";

export default function HistoryPage() {
  const lang = useLanguageStore((s) => s.language);

  return (
    <div>
      <SectionTitle title={t("nav.history", lang)} />

      <Card>
        <h3>Execution History</h3>
        <p>Past pipeline runs will appear here.</p>
      </Card>
    </div>
  );
}
