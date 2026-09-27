import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://127.0.0.1:5173",
  },
  webServer: {
    command: "npm run dev -- --host 127.0.0.1",
    url: process.env.E2E_BASE_URL ?? "http://127.0.0.1:5173",
    reuseExistingServer: !process.env.CI,
  },
  reporter: "line",
});
