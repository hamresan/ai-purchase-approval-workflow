import { expect, test } from "@playwright/test";

async function fillRequest(page: import("@playwright/test").Page): Promise<void> {
  await page.goto("/requests/new");
  await page.getByLabel("What do you want to purchase?").fill("Dana needs one laptop stand");
}

test("validation fallback remains actionable in the browser", async ({ page }) => {
  await page.route("**/api/purchase-requests", async (route) => {
    if (route.request().method() !== "POST") {
      await route.continue();
      return;
    }
    await route.fulfill({
      status: 422,
      contentType: "application/json",
      body: JSON.stringify({ detail: "The request needs more information before it can continue." }),
    });
  });

  await fillRequest(page);
  await page.getByRole("button", { name: /Submit Request/ }).click();

  await expect(page.getByRole("alert")).toContainText("needs more information");
  await expect(page.getByRole("button", { name: /Submit Request/ })).toBeEnabled();
});

test("unexpected backend failure does not show a false success state", async ({ page }) => {
  await page.route("**/api/purchase-requests", async (route) => {
    if (route.request().method() !== "POST") {
      await route.continue();
      return;
    }
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Unable to process the purchase request." }),
    });
  });

  await fillRequest(page);
  await page.getByRole("button", { name: /Submit Request/ }).click();

  await expect(page.getByRole("alert")).toContainText("Unable to process");
  await expect(page.getByRole("heading", { name: "Your request has been submitted" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: /Submit Request/ })).toBeEnabled();
});
