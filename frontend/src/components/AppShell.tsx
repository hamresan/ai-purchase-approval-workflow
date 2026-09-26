import type { ReactNode } from "react";

import type { AppRoute } from "@/app/navigation";

interface AppShellProps {
  route: AppRoute;
  onNavigate: (route: AppRoute) => void;
  children: ReactNode;
}

export function AppShell({ route, onNavigate, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand"><span className="brand-mark">🛒</span><strong>AI Purchase<br />Approval</strong></div>
        <nav>
          <button className={route === "requests" ? "nav-item active" : "nav-item"} onClick={() => onNavigate("requests")}>▣ <span>Purchase Requests</span></button>
          <button className={route === "new-request" ? "nav-item active" : "nav-item"} onClick={() => onNavigate("new-request")}>＋ <span>New Purchase Request</span></button>
        </nav>
      </aside>
      <div className="app-content">
        <header className="topbar">
          <div className="mobile-brand"><span>🛒</span><strong>AI Purchase Approval</strong></div>
          <span className="app-context">Purchase workspace</span>
        </header>
        <main>{children}</main>
      </div>
    </div>
  );
}
