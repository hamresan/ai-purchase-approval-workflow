import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

function testDatabaseUrl(): string {
  if (process.env.TEST_DATABASE_URL) return process.env.TEST_DATABASE_URL;
  const envFile = readFileSync(resolve(process.cwd(), "../.env"), "utf8");
  const line = envFile.split(/\r?\n/).find((entry) => entry.startsWith("TEST_DATABASE_URL="));
  if (!line) throw new Error("TEST_DATABASE_URL must be configured for E2E tests.");
  return line.slice("TEST_DATABASE_URL=".length).trim();
}

export function seedPendingRequest(): string {
  const { VIRTUAL_ENV: _virtualEnv, ...environment } = process.env;
  environment.TEST_DATABASE_URL = testDatabaseUrl();

  const output = execFileSync(
    "uv",
    ["run", "--directory", "../backend", "python", "tests/e2e/support/seed_pending_request.py"],
    { encoding: "utf8", env: environment },
  );

  return output.trim().split(/\r?\n/).at(-1) ?? "";
}
