/**
 * env-check.ts — Runtime environment variable validation
 * Imported at the top of the Next.js app bootstrap to catch misconfigurations early.
 */

type EnvVarSpec = {
  name: string;
  required: boolean;
  serverOnly?: boolean;
  warnIfPlaceholder?: string[];
};

const ENV_VARS: EnvVarSpec[] = [
  { name: "NEXT_PUBLIC_API_URL", required: true },
  { name: "NEXT_PUBLIC_API_KEY", required: true, warnIfPlaceholder: ["change-this-in-prod", "6398feff333542007b3e100af5029c65"] },
  { name: "AUTH_SECRET", required: true, serverOnly: true, warnIfPlaceholder: ["super-secret-nextauth-replace-in-prod-32chars"] },
  { name: "AUTH_GOOGLE_ID", required: false, serverOnly: true, warnIfPlaceholder: ["your-google-client-id-here"] },
  { name: "AUTH_GOOGLE_SECRET", required: false, serverOnly: true, warnIfPlaceholder: ["your-google-client-secret-here"] },
  { name: "AUTH_GITHUB_ID", required: false, serverOnly: true, warnIfPlaceholder: ["your-github-client-id-here"] },
  { name: "AUTH_GITHUB_SECRET", required: false, serverOnly: true, warnIfPlaceholder: ["your-github-client-secret-here"] },
];

export function validateEnv(): void {
  // Only run this check on the server side
  if (typeof window !== "undefined") return;

  const missing: string[] = [];
  const warnings: string[] = [];

  for (const spec of ENV_VARS) {
    const value = process.env[spec.name];

    if (spec.required && (!value || value.trim() === "")) {
      missing.push(`  ✗ ${spec.name} — required but not set`);
      continue;
    }

    if (value && spec.warnIfPlaceholder?.includes(value)) {
      warnings.push(`  ⚠  ${spec.name} is still set to a placeholder value: "${value}"`);
    }
  }

  if (missing.length > 0) {
    throw new Error(
      `\n\n❌ Missing required environment variables:\n${missing.join("\n")}\n\nSet them in frontend/.env.local\n`
    );
  }

  if (warnings.length > 0) {
    console.warn(
      `\n⚠️  Environment variable warnings:\n${warnings.join("\n")}\n`
    );
  }
}
