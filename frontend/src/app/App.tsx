import { useCallback, useEffect, useMemo, useState } from "react";
import { AuthorizedHttpClient } from "@/api/httpClient";
import { HttpPurchaseRequestApi } from "@/api/purchaseRequests";
import { HttpPurchaseRequestApprovalApi } from "@/api/purchaseRequestApproval";
import { HttpPurchaseRequestSubmissionApi } from "@/api/purchaseRequestSubmission";
import { pathForRequestDetail, pathForRoute, requestIdFromPath, routeFromPath, type AppRoute } from "@/app/navigation";
import { HttpIdentityAuthApi } from "@/auth/api";
import { BrowserAuthSessionStore, type AuthSession } from "@/auth/session";
import { AppShell } from "@/components/AppShell";
import { AuthScreen } from "@/features/auth/AuthScreen";
import { NewPurchaseRequest } from "@/features/requests/NewPurchaseRequest";
import { RequestDashboard } from "@/features/requests/RequestDashboard";
import { RequestDetail } from "@/features/requests/RequestDetail";
import "@/app/styles.css";

export function App() {
  const sessionStore = useMemo(() => new BrowserAuthSessionStore(), []);
  const [session, setSession] = useState<AuthSession | null>(() => sessionStore.load());
  const e2eMode = import.meta.env.VITE_E2E_AUTH_BYPASS === "true";
  const [route, setRoute] = useState<AppRoute>(() => routeFromPath(window.location.pathname));
  const [requestId, setRequestId] = useState<string | null>(() => requestIdFromPath(window.location.pathname));
  const http = useMemo(() => e2eMode ? { fetch: (input: RequestInfo | URL, init?: RequestInit) => fetch(input, init) } : new AuthorizedHttpClient({ getAccessToken: () => session?.accessToken ?? null }), [e2eMode, session]);
  const requestApi = useMemo(() => new HttpPurchaseRequestApi("", http), [http]);
  const submissionApi = useMemo(() => new HttpPurchaseRequestSubmissionApi("", http), [http]);
  const approvalApi = useMemo(() => new HttpPurchaseRequestApprovalApi("", http), [http]);
  const authApi = useMemo(() => new HttpIdentityAuthApi(), []);

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
  const signOut = () => { sessionStore.clear(); setSession(null); };

  if (!session && !e2eMode) return <AuthScreen api={authApi} onAuthenticated={authenticated} />;
  return <AppShell route={route} onNavigate={navigate} onSignOut={signOut}>
    {route === "new-request" && <NewPurchaseRequest api={submissionApi} onBack={() => navigate("requests")} />}
    {route === "request-detail" && requestId && <RequestDetail api={requestApi} approvalApi={approvalApi} requestId={requestId} onBack={() => navigate("requests")} />}
    {route === "requests" && <RequestDashboard api={requestApi} onNewRequest={() => navigate("new-request")} onOpenRequest={openRequest} />}
  </AppShell>;
}
