import { useCallback, useEffect, useMemo, useState } from "react";

import { HttpPurchaseRequestApi } from "@/api/purchaseRequests";
import { HttpPurchaseRequestSubmissionApi } from "@/api/purchaseRequestSubmission";
import { pathForRequestDetail, pathForRoute, requestIdFromPath, routeFromPath, type AppRoute } from "@/app/navigation";
import { AppShell } from "@/components/AppShell";
import { NewPurchaseRequest } from "@/features/requests/NewPurchaseRequest";
import { RequestDashboard } from "@/features/requests/RequestDashboard";
import { RequestDetail } from "@/features/requests/RequestDetail";
import "@/app/styles.css";

export function App() {
  const [route, setRoute] = useState<AppRoute>(() => routeFromPath(window.location.pathname));
  const [requestId, setRequestId] = useState<string | null>(() => requestIdFromPath(window.location.pathname));
  const requestApi = useMemo(() => new HttpPurchaseRequestApi(), []);
  const submissionApi = useMemo(() => new HttpPurchaseRequestSubmissionApi(), []);

  useEffect(() => {
    const syncRoute = () => {
      setRoute(routeFromPath(window.location.pathname));
      setRequestId(requestIdFromPath(window.location.pathname));
    };
    window.addEventListener("popstate", syncRoute);
    return () => window.removeEventListener("popstate", syncRoute);
  }, []);

  const navigate = useCallback((nextRoute: Exclude<AppRoute, "request-detail">) => {
    window.history.pushState({}, "", pathForRoute(nextRoute));
    setRequestId(null);
    setRoute(nextRoute);
  }, []);

  const openRequest = useCallback((id: string) => {
    window.history.pushState({}, "", pathForRequestDetail(id));
    setRequestId(id);
    setRoute("request-detail");
  }, []);

  return (
    <AppShell route={route} onNavigate={navigate}>
      {route === "new-request" && <NewPurchaseRequest api={submissionApi} onBack={() => navigate("requests")} />}
      {route === "request-detail" && requestId && <RequestDetail api={requestApi} requestId={requestId} onBack={() => navigate("requests")} />}
      {route === "requests" && <RequestDashboard api={requestApi} onNewRequest={() => navigate("new-request")} onOpenRequest={openRequest} />}
    </AppShell>
  );
}
