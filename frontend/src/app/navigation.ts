export type AppRoute = "requests" | "new-request";

export function routeFromPath(pathname: string): AppRoute {
  return pathname === "/requests/new" ? "new-request" : "requests";
}

export function pathForRoute(route: AppRoute): string {
  return route === "new-request" ? "/requests/new" : "/requests";
}
