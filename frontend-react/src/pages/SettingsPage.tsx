import { Card } from "../components/ui/Card";
import { SectionTitle } from "../components/ui/SectionTitle";
import { Input } from "../components/ui/Input";
import { t } from "../i18n";
import { useLanguageStore } from "../state/languageState";

export default function SettingsPage() {
  const lang = useLanguageStore((s) => s.language);

  return (
    <div>
      <SectionTitle title={t("nav.settings", lang)} />

      <Card>
        <h3>System Settings</h3>
        <Input placeholder="Setting value..." />
      </Card>
    </div>
  );
}
