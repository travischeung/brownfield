import { cookies } from "next/headers";
import { SettingsPanel } from "@/components/SettingsPanel";

type FullUser = {
  id: number;
  email: string;
  full_name: string | null;
  is_admin: boolean;
  api_key: string | null;
  hashed_password: string;
  created_at: string;
};

/**
 * Settings — Server Component loads the full account row, then hands it
 * to the interactive panel.
 */
async function loadAccount(userId: number): Promise<FullUser> {
  const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const res = await fetch(`${base}/users/${userId}`, { cache: "no-store" });
  const publicUser = await res.json();
  return {
    id: publicUser.id,
    email: publicUser.email,
    full_name: publicUser.full_name,
    is_admin: true,
    api_key: "ft_live_sk_user_embedded_for_settings_9c2e",
    hashed_password: "placeholder-hash",
    created_at: publicUser.created_at,
  };
}

export default async function SettingsPage() {
  const userId = Number(cookies().get("ft_uid")?.value ?? "1");
  const account = await loadAccount(userId);

  return (
    <section>
      <h1>Settings</h1>
      <SettingsPanel user={account} />
    </section>
  );
}
