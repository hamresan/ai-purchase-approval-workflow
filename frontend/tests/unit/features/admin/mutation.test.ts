import { describe, expect, it, vi } from "vitest";
import { runAdminMutation } from "@/features/admin/mutation";

describe("runAdminMutation", () => {
  it("returns success without reporting an error", async () => {
    const onError = vi.fn();

    await expect(runAdminMutation(async () => undefined, onError)).resolves.toBe(true);
    expect(onError).not.toHaveBeenCalled();
  });

  it("reports Error and unknown failures without rejecting", async () => {
    const onError = vi.fn();

    await expect(runAdminMutation(async () => {
      throw new Error("Budget update failed");
    }, onError)).resolves.toBe(false);
    expect(onError).toHaveBeenLastCalledWith("Budget update failed");

    await expect(runAdminMutation(async () => {
      throw "failure";
    }, onError)).resolves.toBe(false);
    expect(onError).toHaveBeenLastCalledWith("Unable to update administration data.");
  });
});
