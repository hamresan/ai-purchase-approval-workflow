import { useCallback, useEffect, useMemo, useState } from "react";
import { AuthorizedHttpClient } from "@/api/httpClient";
import { HttpAdminApi } from "@/api/admin";
import { HttpPurchaseRequestApi } from "@/api/purchaseRequests";
import { HttpPurchaseRequestApprovalApi } from "@/api/purchaseRequestApproval";
import { HttpPurchaseRequestSubmissionApi } from "@/api/purchaseRequestSubmission";
import { pathForRequestDetail, pathForRoute, requestIdFromPath, routeFromPath, type AppRoute } from "@/app/navigation";
import { HttpIdentityAuthApi } from "@/auth/api";
import { BrowserAuthSessionStore, type AuthSession } from "@/auth/session";
import { AppShell } from "@/components/AppShell";
import { AuthScreen } from "@/features/auth/AuthScreen";
import { AdminManagement } from "@/features/admin/AdminManagement";
import { NewPurchaseRequest } from "@/features/requests/NewPurchaseRequest";
import { RequestDashboard } from "@/features/requests/RequestDashboard";
import { RequestDetail } from "@/features/requests/RequestDetail";
import "@/app/styles.css";

export function App() {
  const sessionStore = useMemo(() => new BrowserAuthSessionStore(), []);
  const [session, setSession] = useState<AuthSession | null>(() => sessionStore.load());
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null);
  const e2eMode = import.meta.env.VITE_E2E_AUTH_BYPASS === "true";
  const [route, setRoute] = useState<AppRoute>(() => routeFromPath(window.location.pathname));
  const [requestId, setRequestId] = useState<string | null>(() => requestIdFromPath(window.location.pathname));
  const authApi = useMemo(() => new HttpIdentityAuthApi(), []);
  const http = useMemo(() => e2eMode ? { fetch: (input: RequestInfo | URL, init?: RequestInit) => fetch(input, init) } : new AuthorizedHttpClient({
    getSession: () => sessionStore.load(),
    refreshSession: async () => {
      const current = sessionStore.load();
      if (!current) throw new Error("Authentication is required.");
      const refreshed = await authApi.refreshSession(current.refreshToken);
      sessionStore.save(refreshed);
      setSession(refreshed);
      return refreshed;
    },
    clearSession: () => {
      sessionStore.clear();
      setSession(null);
    },
  }), [authApi, e2eMode, sessionStore]);
  const adminApi = useMemo(() => new HttpAdminApi(http), [http]);
  useEffect(() => {
    if (!session && !e2eMode) { setIsAdmin(null); return; }
    setIsAdmin(null);
    void http.fetch("/api/profile").then(async response => {
      if (!response.ok) return;
      const profile = await response.json() as { roles?: string[] };
      setIsAdmin(profile.roles?.includes("admin") === true);
    }).catch(() => setIsAdmin(false));
  }, [e2eMode, http, session]);

  const requestApi = useMemo(() => new HttpPurchaseRequestApi("", http), [http]);
  const submissionApi = useMemo(() => new HttpPurchaseRequestSubmissionApi("", http), [http]);
  const approvalApi = useMemo(() => new HttpPurchaseRequestApprovalApi("", http), [http]);

  useEffect(() => {
    const syncRoute = () => { setRoute(routeFromPath(window.location.pathname)); setRequestId(requestIdFromPath(window.location.pathname)); };
    window.addEventListener("popstate", syncRoute);
    return () => window.removeEventListener("popstate", syncRoute);
  }, []);

  const navigate = useCallback((nextRoute: Exclude<AppRoute, "request-detail">) => {
    window.history.pushState({}, "", pathForRoute(nextRoute)); setRequestId(null); setRoute(nextRoute);
  }, []);
  const openRequest = useCallback((id: string) => {
    window.history.pushState({}, "", pathForRequestDetail(id)); setRequestId(id); setRoute("request-detail");
  }, []);
  const authenticated = (value: AuthSession) => { sessionStore.save(value); setSession(value); window.history.replaceState({}, "", "/requests"); setRoute("requests"); setRequestId(null); };
  const signOut = () => {
    const current = sessionStore.load();
    sessionStore.clear();
    setSession(null);
    if (current) void authApi.revokeSession(current.refreshToken).catch(() => undefined);
  };

  if (!session && !e2eMode) return <AuthScreen api={authApi} onAuthenticated={authenticated} />;
  return <AppShell route={route} isAdmin={isAdmin === true} onNavigate={navigate} onSignOut={signOut}>
    {route === "admin" && isAdmin === null && <section className="page"><div className="state-panel"><div className="spinner" aria-hidden="true" /><h2>Loading administrator access…</h2></div></section>}
    {route === "admin" && isAdmin === true && <AdminManagement api={adminApi} />}
    {route === "new-request" && <NewPurchaseRequest api={submissionApi} onBack={() => navigate("requests")} />}
    {route === "request-detail" && requestId && <RequestDetail api={requestApi} approvalApi={approvalApi} requestId={requestId} onBack={() => navigate("requests")} />}
    {route === "requests" && <RequestDashboard api={requestApi} onNewRequest={() => navigate("new-request")} onOpenRequest={openRequest} />}
  </AppShell>;
}
