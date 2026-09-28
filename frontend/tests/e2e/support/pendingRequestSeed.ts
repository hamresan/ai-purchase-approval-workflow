import { expect, type Page } from "@playwright/test";

interface CreatedPurchaseRequest {
  id?: unknown;
}

export async function seedPendingRequest(page: Page): Promise<string> {
  const response = await page.request.post("/api/purchase-requests", {
    data: {
      request_text: "Dana needs one laptop stand",
    },
  });

  if (!response.ok()) {
    throw new Error(
      `Unable to seed pending request through API: ${response.status()} ${await response.text()}`,
    );
  }

  const payload = (await response.json()) as CreatedPurchaseRequest;
  expect(typeof payload.id).toBe("string");
  return payload.id as string;
}
