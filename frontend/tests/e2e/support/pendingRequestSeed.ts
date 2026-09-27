import { expect, type Page } from "@playwright/test";

export async function seedPendingRequest(page: Page): Promise<string> {
  const response = await page.request.post("/api/purchase-requests", {
    data: {
      request_text: "Dana needs one laptop stand",
      requester_name: "Dana",
    },
  });

  expect(response.ok()).toBeTruthy();
  const payload = (await response.json()) as { id?: unknown };
  expect(typeof payload.id).toBe("string");
  return payload.id as string;
}
