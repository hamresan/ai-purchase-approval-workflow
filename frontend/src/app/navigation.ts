export type AppRoute = "requests" | "new-request" | "request-detail" | "admin";

export function routeFromPath(pathname: string): AppRoute {
  if (pathname === "/admin") return "admin";
  if (pathname === "/requests/new") return "new-request";
  if (/^\/requests\/[^/]+$/.test(pathname)) return "request-detail";
  return "requests";
}

export function requestIdFromPath(pathname: string): string | null {
  if (routeFromPath(pathname) !== "request-detail") return null;
  return decodeURIComponent(pathname.slice("/requests/".length));
}

export function pathForRoute(route: Exclude<AppRoute, "request-detail">): string {
  if (route === "new-request") return "/requests/new";
  if (route === "admin") return "/admin";
  return "/requests";
}

export function pathForRequestDetail(requestId: string): string {
  return `/requests/${encodeURIComponent(requestId)}`;
}
