import { FormEvent, useEffect, useState } from "react";
import { Save } from "lucide-react";
import { Status } from "../../components/Status";
import { api } from "../../services/api";

interface Props {
  onShopName: (value: string) => void;
}

export function SettingsPage({ onShopName }: Props) {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    api.settings().then(setSettings).catch((err) => setError(err.message));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setSuccess("");
    try {
      await Promise.all(Object.entries(settings).map(([key, value]) => api.saveSetting(key, value)));
      onShopName(settings.shop_name ?? "Dairy Shop");
      setSuccess("Settings saved");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save settings");
    }
  }

  function update(key: string, value: string) {
    setSettings((current) => ({ ...current, [key]: value }));
  }

  return (
    <section className="page">
      <div className="page-title"><div><h1>Settings</h1><p>Basic shop configuration for V1.</p></div></div>
      <Status error={error} success={success} />
      <form className="panel form-grid settings-form" onSubmit={submit}>
        <label>Shop name<input value={settings.shop_name ?? ""} onChange={(e) => update("shop_name", e.target.value)} /></label>
        <label>Currency display<input value={settings.currency ?? "KSh"} onChange={(e) => update("currency", e.target.value)} /></label>
        <label>Default milk unit<input value={settings.default_milk_unit ?? "Litre"} onChange={(e) => update("default_milk_unit", e.target.value)} /></label>
        <label>Milk measurement precision<input type="number" min="0" max="4" value={settings.measurement_precision_ml ?? "2"} onChange={(e) => update("measurement_precision_ml", e.target.value)} /></label>
        <button className="primary"><Save size={18} />Save Settings</button>
      </form>
    </section>
  );
}
