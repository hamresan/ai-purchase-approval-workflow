import { pathForRoute, routeFromPath } from "@/app/navigation";

describe("navigation", () => {
  it("maps known application routes", () => {
    expect(routeFromPath("/requests/new")).toBe("new-request");
    expect(routeFromPath("/requests")).toBe("requests");
    expect(routeFromPath("/anything")).toBe("requests");
    expect(pathForRoute("new-request")).toBe("/requests/new");
    expect(pathForRoute("requests")).toBe("/requests");
  });
});
