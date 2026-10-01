import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import type { HttpAdminApi } from "@/api/admin";
import { RoleManagement } from "@/features/admin/RoleManagement";

function renderRoles(replaceRoles: HttpAdminApi["replaceRoles"]) {
  const api = { replaceRoles } as HttpAdminApi;
  const onChanged = vi.fn();
  render(
    <RoleManagement
      api={api}
      assignments={[{ user_id: "user-1", roles: ["requester", "admin"] }]}
      onChanged={onChanged}
    />,
  );
  return onChanged;
}

describe("RoleManagement", () => {
  it("removes an assigned role and publishes the updated assignment", async () => {
    const replaceRoles = vi.fn().mockResolvedValue({
      user_id: "user-1",
      roles: ["requester"],
    });
    const onChanged = renderRoles(replaceRoles);

    fireEvent.click(screen.getByRole("checkbox", { name: "Admin" }));

    await waitFor(() =>
      expect(replaceRoles).toHaveBeenCalledWith("user-1", ["requester"]),
    );
    expect(onChanged).toHaveBeenCalledWith([
      { user_id: "user-1", roles: ["requester"] },
    ]);
  });

  it("adds a role", async () => {
    const replaceRoles = vi.fn().mockResolvedValue({
      user_id: "user-1",
      roles: ["requester", "admin", "approver"],
    });
    renderRoles(replaceRoles);

    fireEvent.click(screen.getByRole("checkbox", { name: "Approver" }));

    await waitFor(() => expect(replaceRoles).toHaveBeenCalled());
  });

  it("keeps at least one role", () => {
    const api = { replaceRoles: vi.fn() } as unknown as HttpAdminApi;
    render(
      <RoleManagement
        api={api}
        assignments={[{ user_id: "user-1", roles: ["requester"] }]}
        onChanged={vi.fn()}
      />,
    );

    fireEvent.click(screen.getByRole("checkbox", { name: "Requester" }));

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Each user must keep at least one application role.",
    );
    expect(api.replaceRoles).not.toHaveBeenCalled();
  });

  it("shows API errors and restores controls", async () => {
    const replaceRoles = vi.fn().mockRejectedValue(new Error("Update failed"));
    renderRoles(replaceRoles);

    fireEvent.click(screen.getByRole("checkbox", { name: "Admin" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Update failed");
    expect(screen.getByRole("checkbox", { name: "Admin" })).not.toBeDisabled();
  });

  it("handles non-Error failures", async () => {
    const replaceRoles = vi.fn().mockRejectedValue("failure");
    renderRoles(replaceRoles);

    fireEvent.click(screen.getByRole("checkbox", { name: "Admin" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Unable to update user roles.",
    );
  });
});
