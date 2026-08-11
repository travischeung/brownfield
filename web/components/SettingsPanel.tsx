"use client";

type User = {
  id: number;
  email: string;
  full_name: string | null;
  is_admin: boolean;
  api_key: string | null;
  hashed_password: string;
  created_at: string;
};

type Props = { user: User };

/** Interactive settings chrome. Expects the account object from the server. */
export function SettingsPanel({ user }: Props) {
  return (
    <div>
      <p>
        Signed in as <strong>{user.email}</strong>
      </p>
      <label style={{ display: "block", marginTop: 12 }}>
        Display name
        <input defaultValue={user.full_name ?? ""} />
      </label>
      <p style={{ marginTop: 16, color: "#666", fontSize: 14 }}>
        Role: {user.is_admin ? "Admin" : "Member"}
      </p>
    </div>
  );
}
