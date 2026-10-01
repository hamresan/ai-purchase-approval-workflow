import { expect, test } from "@playwright/test";

test("admin manages trusted catalog data from the browser", async ({ page }) => {
  await page.setExtraHTTPHeaders({ "X-E2E-Actor": "admin" });
  await page.goto("/admin");

  await expect(page.getByRole("heading", { name: "Admin Management" })).toBeVisible();

  const suffix = Date.now().toString();
  const productName = `E2E product ${suffix}`;
  const vendorName = `E2E vendor ${suffix}`;
  const departmentName = `E2E department ${suffix}`;

  await page.getByLabel("New Product").fill(productName);
  await page.getByRole("button", { name: "Add", exact: true }).nth(1).click();
  await expect(page.getByRole("cell", { name: productName })).toBeVisible();

  await page.getByLabel("New Vendor").fill(vendorName);
  await page.getByRole("button", { name: "Add", exact: true }).nth(2).click();
  await expect(page.getByRole("cell", { name: vendorName })).toBeVisible();

  await page.getByLabel("New Department").fill(departmentName);
  await page.getByRole("button", { name: "Add", exact: true }).first().click();
  await expect(page.getByRole("cell", { name: departmentName })).toBeVisible();

  await page.getByLabel("Product", { exact: true }).selectOption({ label: productName });
  await page.getByLabel("Vendor", { exact: true }).selectOption({ label: vendorName });
  await page.getByLabel("Price").fill("49.90");
  await page.getByLabel("Currency", { exact: true }).fill("usd");
  await page.getByLabel("Available quantity").fill("7");
  await page.getByRole("button", { name: "Add offer" }).click();

  const offerRow = page.getByRole("row").filter({ hasText: productName }).filter({ hasText: vendorName });
  await expect(offerRow).toContainText("USD 49.90");
  await expect(offerRow).toContainText("7");

  await page.getByLabel("Budget owner").selectOption({ label: departmentName });
  await page.getByLabel("Budget amount").fill("1200");
  await page.getByLabel("Budget currency").fill("usd");
  await page.getByRole("button", { name: "Add budget" }).click();

  const budgetRow = page.getByRole("row").filter({ hasText: departmentName });
  await expect(budgetRow).toContainText("USD");
  await expect(budgetRow).toContainText("1200");
});

test("requester cannot access admin management", async ({ page }) => {
  await page.setExtraHTTPHeaders({ "X-E2E-Actor": "requester" });
  await page.goto("/admin");

  await expect(page.getByRole("heading", { name: "Admin Management" })).not.toBeVisible();
  await expect(page.getByText("Admin Management", { exact: true })).not.toBeVisible();

  const response = await page.request.post("/api/admin/products", {
    headers: { "X-E2E-Actor": "requester" },
    data: { name: `Forbidden product ${Date.now()}` },
  });
  expect(response.status()).toBe(403);
});
