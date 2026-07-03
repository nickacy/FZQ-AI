import { Card } from "../components/ui/Card";
import { SectionTitle } from "../components/ui/SectionTitle";
import { t } from "../i18n";
import { useLanguageStore } from "../state/languageState";

export default function FavoritesPage() {
  const lang = useLanguageStore((s) => s.language);

  return (
    <div>
      <SectionTitle title={t("nav.favorites", lang)} />

      <Card>
        <h3>Favorite Items</h3>
        <p>Your saved items will appear here.</p>
      </Card>
    </div>
  );
}
