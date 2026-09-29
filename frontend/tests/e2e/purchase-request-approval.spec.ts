import { expect, test, type Page } from "@playwright/test";

import { seedPendingRequest } from "./support/pendingRequestSeed";

async function openPendingRequest(page: Page, requestId: string): Promise<void> {
  await page.goto(`/requests/${requestId}`);
  await expect(page.getByRole("heading", { name: "Laptop stand" })).toBeVisible();
  await expect(page.getByText("Waiting for approval")).toBeVisible();
}

test("approve submits the order and updates the timeline", async ({ page }) => {
  const requestId = await seedPendingRequest(page);
  await openPendingRequest(page, requestId);
  await page.getByRole("button", { name: /Approve/ }).click();
  await page.getByPlaceholder("Add a comment...").fill("Approved in browser");
  await page.getByRole("button", { name: "Approve", exact: true }).click();
  await expect(page.getByText("Order submitted")).toBeVisible();
  await expect(page.locator(".detail-title").getByText("Submitted", { exact: true })).toBeVisible();
});

test("reject records the reason and updates the timeline", async ({ page }) => {
  const requestId = await seedPendingRequest(page);
  await openPendingRequest(page, requestId);
  await page.getByRole("button", { name: /Reject/ }).click();
  await page.getByPlaceholder("Please provide a reason for rejection...").fill("Budget priority changed");
  await page.getByRole("button", { name: "Reject", exact: true }).click();
  await expect(page.getByText("Request rejected")).toBeVisible();
  await expect(page.locator(".detail-title").getByText("Rejected", { exact: true })).toBeVisible();
});

test("edit revalidates the draft and returns to approval review", async ({ page }) => {
  const requestId = await seedPendingRequest(page);
  await openPendingRequest(page, requestId);
  await page.getByRole("button", { name: /Edit/ }).click();
  await page.getByLabel("Item 1 quantity").fill("2");
  await page.getByRole("button", { name: "Save changes" }).click();
  await expect(page.getByText("Request updated")).toBeVisible();
  await expect(page.getByText("Waiting for approval")).toBeVisible();
  await expect(page.getByRole("button", { name: /Approve/ })).toBeVisible();
});
