import type { Page } from "@playwright/test";

export async function authenticateForE2e(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem(
      "purchase-approval.auth-session",
      JSON.stringify({ userId: "e2e-user", accessToken: "e2e-access-token", refreshToken: "e2e-refresh-token" }),
    );
  });
}
