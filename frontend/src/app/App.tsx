import { useCallback, useMemo, useState } from "react";

import { HttpPurchaseRequestApi } from "@/api/purchaseRequests";
import { HttpPurchaseRequestSubmissionApi } from "@/api/purchaseRequestSubmission";
import { pathForRoute, routeFromPath, type AppRoute } from "@/app/navigation";
import { AppShell } from "@/components/AppShell";
import { NewPurchaseRequest } from "@/features/requests/NewPurchaseRequest";
import { RequestDashboard } from "@/features/requests/RequestDashboard";
import "@/app/styles.css";

export function App() {
  const [route, setRoute] = useState<AppRoute>(() => routeFromPath(window.location.pathname));
  const requestApi = useMemo(() => new HttpPurchaseRequestApi(), []);
  const submissionApi = useMemo(() => new HttpPurchaseRequestSubmissionApi(), []);

  const navigate = useCallback((nextRoute: AppRoute) => {
    window.history.pushState({}, "", pathForRoute(nextRoute));
    setRoute(nextRoute);
  }, []);

  return (
    <AppShell route={route} onNavigate={navigate}>
      {route === "new-request"
        ? <NewPurchaseRequest api={submissionApi} onBack={() => navigate("requests")} />
        : <RequestDashboard api={requestApi} onNewRequest={() => navigate("new-request")} />}
    </AppShell>
  );
}
