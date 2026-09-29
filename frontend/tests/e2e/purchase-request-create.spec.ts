import { expect, test } from "@playwright/test";


test("create request runs the workflow and can be approved from the browser", async ({ page }) => {
  await page.setExtraHTTPHeaders({ "X-E2E-Actor": "requester" });
  let createdRequestId: string | undefined;
  page.on("response", async (response) => {
    if (
      response.request().method() === "POST"
      && new URL(response.url()).pathname === "/api/purchase-requests"
      && response.ok()
    ) {
      const payload = (await response.json()) as { id?: unknown; request_id?: unknown };
      const requestId = payload.request_id ?? payload.id;
      if (typeof requestId === "string") createdRequestId = requestId;
    }
  });

  await page.goto("/requests/new");
  await page.getByLabel("What do you want to purchase?").fill("Dana needs one laptop stand");
  await page.getByRole("button", { name: /Submit Request/ }).click();

  await expect(page.getByRole("heading", { name: "Your request has been submitted" })).toBeVisible();
  expect(createdRequestId).toBeTruthy();

  await page.setExtraHTTPHeaders({ "X-E2E-Actor": "approver" });
  await page.goto(`/requests/${createdRequestId}`);
  await expect(page.getByText("Waiting for approval")).toBeVisible();
  await page.getByRole("button", { name: /Approve/ }).click();
  await page.getByRole("button", { name: "Approve", exact: true }).click();

  await expect(page.locator(".detail-title").getByText("Submitted", { exact: true })).toBeVisible();
  await expect(page.getByText("Order submitted")).toBeVisible();
});
