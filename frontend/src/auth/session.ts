export interface AuthSession {
  userId: string;
  accessToken: string;
  refreshToken: string;
}

export interface AuthSessionStore {
  load(): AuthSession | null;
  save(session: AuthSession): void;
  clear(): void;
}

const SESSION_KEY = "purchase-approval.auth-session";

export class BrowserAuthSessionStore implements AuthSessionStore {
  load(): AuthSession | null {
    const value = window.localStorage.getItem(SESSION_KEY);
    if (!value) return null;
    try {
      const parsed = JSON.parse(value) as Partial<AuthSession>;
      if (
        typeof parsed.userId === "string"
        && typeof parsed.accessToken === "string"
        && typeof parsed.refreshToken === "string"
      ) {
        return {
          userId: parsed.userId,
          accessToken: parsed.accessToken,
          refreshToken: parsed.refreshToken,
        };
      }
    } catch {
      // Invalid local state is treated as signed out.
    }
    return null;
  }

  save(session: AuthSession): void {
    window.localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  }

  clear(): void {
    window.localStorage.removeItem(SESSION_KEY);
  }
}
