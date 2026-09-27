import { pathForRequestDetail, pathForRoute, requestIdFromPath, routeFromPath } from "@/app/navigation";

describe("navigation", () => {
  it("maps application routes to and from paths", () => {
    expect(routeFromPath("/requests")).toBe("requests");
    expect(routeFromPath("/requests/new")).toBe("new-request");
    expect(routeFromPath("/requests/abc-123")).toBe("request-detail");
    expect(requestIdFromPath("/requests/abc-123")).toBe("abc-123");
    expect(requestIdFromPath("/requests")).toBeNull();
    expect(pathForRoute("requests")).toBe("/requests");
    expect(pathForRoute("new-request")).toBe("/requests/new");
    expect(pathForRequestDetail("abc 123")).toBe("/requests/abc%20123");
  });
});
