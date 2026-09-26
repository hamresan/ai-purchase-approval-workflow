import { useCallback, useMemo, useState } from "react";

import { HttpPurchaseRequestApi } from "@/api/purchaseRequests";
import { AppShell } from "@/components/AppShell";
import { NewPurchaseRequest } from "@/features/requests/NewPurchaseRequest";
import { RequestDashboard } from "@/features/requests/RequestDashboard";
import { pathForRoute, routeFromPath, type AppRoute } from "@/app/navigation";
import "@/app/styles.css";

export function App() {
  const [route, setRoute] = useState<AppRoute>(() => routeFromPath(window.location.pathname));
  const api = useMemo(() => new HttpPurchaseRequestApi(), []);

  const navigate = useCallback((nextRoute: AppRoute) => {
    window.history.pushState({}, "", pathForRoute(nextRoute));
    setRoute(nextRoute);
  }, []);

  return (
    <AppShell route={route} onNavigate={navigate}>
      {route === "new-request"
        ? <NewPurchaseRequest onBack={() => navigate("requests")} />
        : <RequestDashboard api={api} onNewRequest={() => navigate("new-request")} />}
    </AppShell>
  );
}
