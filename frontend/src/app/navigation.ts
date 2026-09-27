export type AppRoute = "requests" | "new-request" | "request-detail";

export function routeFromPath(pathname: string): AppRoute {
  if (pathname === "/requests/new") return "new-request";
  if (/^\/requests\/[^/]+$/.test(pathname)) return "request-detail";
  return "requests";
}

export function requestIdFromPath(pathname: string): string | null {
  if (routeFromPath(pathname) !== "request-detail") return null;
  return decodeURIComponent(pathname.slice("/requests/".length));
}

export function pathForRoute(route: Exclude<AppRoute, "request-detail">): string {
  return route === "new-request" ? "/requests/new" : "/requests";
}

export function pathForRequestDetail(requestId: string): string {
  return `/requests/${encodeURIComponent(requestId)}`;
}
