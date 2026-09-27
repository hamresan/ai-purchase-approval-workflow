import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

const backendUrl = process.env.E2E_BACKEND_URL ?? "http://127.0.0.1:8000";

async function createPendingRequest(request: APIRequestContext): Promise<string> {
  const created = await request.post(`${backendUrl}/api/purchase-requests`, {
    data: {
      requester_name: "Dana",
      items: [{
        description: "Laptop stand",
        quantity: 1,
        unit_price_amount: "1.00",
        currency: "USD",
      }],
    },
  });
  expect(created.status()).toBe(201);
  const body = await created.json() as { id: string };
  const prepared = await request.post(`${backendUrl}/api/purchase-requests/${body.id}/prepare`);
  expect(prepared.ok()).toBeTruthy();
  return body.id;
}

async function openPendingRequest(page: Page, requestId: string): Promise<void> {
  await page.goto(`/requests/${requestId}`);
  await expect(page.getByRole("heading", { name: "Laptop stand" })).toBeVisible();
  await expect(page.getByText("Waiting for approval")).toBeVisible();
}

test("approve submits the order and updates the timeline", async ({ page, request }) => {
  const requestId = await createPendingRequest(request);
  await openPendingRequest(page, requestId);
  await page.getByRole("button", { name: /Approve/ }).click();
  await page.getByLabel("Reviewer name").fill("E2E Reviewer");
  await page.getByPlaceholder("Add a comment...").fill("Approved in browser");
  await page.getByRole("button", { name: "Approve", exact: true }).click();
  await expect(page.getByText("Order submitted")).toBeVisible();
  await expect(page.getByText("Submitted", { exact: true })).toBeVisible();
});

test("reject records the reason and updates the timeline", async ({ page, request }) => {
  const requestId = await createPendingRequest(request);
  await openPendingRequest(page, requestId);
  await page.getByRole("button", { name: /Reject/ }).click();
  await page.getByLabel("Reviewer name").fill("E2E Reviewer");
  await page.getByPlaceholder("Please provide a reason for rejection...").fill("Budget priority changed");
  await page.getByRole("button", { name: "Reject", exact: true }).click();
  await expect(page.getByText("Request rejected")).toBeVisible();
  await expect(page.getByText("Rejected", { exact: true })).toBeVisible();
});

test("edit revalidates the draft and returns to approval review", async ({ page, request }) => {
  const requestId = await createPendingRequest(request);
  await openPendingRequest(page, requestId);
  await page.getByRole("button", { name: /Edit/ }).click();
  await page.getByLabel("Reviewer name").fill("E2E Reviewer");
  await page.getByLabel("Item 1 quantity").fill("2");
  await page.getByRole("button", { name: "Save changes" }).click();
  await expect(page.getByText("Request updated")).toBeVisible();
  await expect(page.getByText("Waiting for approval")).toBeVisible();
  await expect(page.getByRole("button", { name: /Approve/ })).toBeVisible();
});
