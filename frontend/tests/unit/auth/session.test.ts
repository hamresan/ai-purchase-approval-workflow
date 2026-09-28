import { BrowserAuthSessionStore } from "@/auth/session";
describe("BrowserAuthSessionStore", () => {
  afterEach(() => window.localStorage.clear());
  it("persists and restores a valid session", () => {
    const store = new BrowserAuthSessionStore();
    const session = { userId: "user-1", accessToken: "access", refreshToken: "refresh" };
    store.save(session);
    expect(store.load()).toEqual(session);
    store.clear();
    expect(store.load()).toBeNull();
  });
  it("ignores malformed local state", () => {
    window.localStorage.setItem("purchase-approval.auth-session", "{bad");
    expect(new BrowserAuthSessionStore().load()).toBeNull();
  });
});
