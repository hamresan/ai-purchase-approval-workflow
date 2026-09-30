import type { ReactNode } from "react";
import type { AppRoute } from "@/app/navigation";

interface AppShellProps { route: AppRoute; onNavigate: (route: Exclude<AppRoute, "request-detail">) => void; onSignOut: () => void; children: ReactNode; }

export function AppShell({ route, onNavigate, onSignOut, children }: AppShellProps) {
  const requestsActive = route === "requests" || route === "request-detail";
  return <div className="app-shell">
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="brand"><span className="brand-mark">🛒</span><strong>AI Purchase<br />Approval</strong></div>
      <nav><button className={requestsActive ? "nav-item active" : "nav-item"} onClick={() => onNavigate("requests")}>▣ <span>Purchase Requests</span></button><button className={route === "new-request" ? "nav-item active" : "nav-item"} onClick={() => onNavigate("new-request")}>＋ <span>New Purchase Request</span></button><button className={route === "admin" ? "nav-item active" : "nav-item"} onClick={() => onNavigate("admin")}>⚙ <span>Admin Management</span></button></nav>
    </aside>
    <div className="app-content"><header className="topbar"><div className="mobile-brand"><span>🛒</span><strong>AI Purchase Approval</strong></div><div className="topbar-actions"><span className="app-context">Purchase workspace</span><button className="sign-out-button" onClick={onSignOut}>Sign out</button></div></header><main>{children}</main></div>
  </div>;
}
