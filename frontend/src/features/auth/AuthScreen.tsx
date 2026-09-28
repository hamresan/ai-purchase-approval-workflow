import { FormEvent, useState } from "react";
import type { AuthPurpose, IdentityAuthApi } from "@/auth/api";
import type { AuthSession } from "@/auth/session";

interface Props { api: IdentityAuthApi; onAuthenticated: (session: AuthSession) => void; }

export function AuthScreen({ api, onAuthenticated }: Props) {
  const [purpose, setPurpose] = useState<AuthPurpose>("login");
  const [challengeId, setChallengeId] = useState("");
  const [mobile, setMobile] = useState("");
  const [fullName, setFullName] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const sendOtp = async (event: FormEvent) => {
    event.preventDefault();
    if (!mobile.trim()) return setError("Enter your mobile number.");
    if (purpose === "registration" && !fullName.trim()) return setError("Enter your full name.");
    setBusy(true); setError("");
    try {
      const challenge = await api.requestOtp(mobile.trim(), purpose);
      setChallengeId(challenge.challengeId);
    } catch (caught) { setError(errorMessage(caught)); } finally { setBusy(false); }
  };

  const verifyOtp = async (event: FormEvent) => {
    event.preventDefault();
    if (!code.trim()) return setError("Enter the verification code.");
    setBusy(true); setError("");
    try {
      onAuthenticated(await api.verifyOtp(challengeId, code.trim(), purpose === "registration" ? fullName.trim() : undefined));
    } catch (caught) { setError(errorMessage(caught)); } finally { setBusy(false); }
  };

  return <main className="auth-page"><section className="auth-card">
    <header className="auth-brand"><span className="brand-mark">🛒</span><strong>Purchase Requests</strong></header>
    {!challengeId ? <>
      <div className="auth-heading"><h1>{purpose === "login" ? "Welcome back" : "Create your account"}</h1><p>Use your mobile number to continue securely with a one-time code.</p></div>
      <div className="auth-mode"><button type="button" className={purpose === "login" ? "active" : ""} onClick={() => setPurpose("login")}>Sign in</button><button type="button" className={purpose === "registration" ? "active" : ""} onClick={() => setPurpose("registration")}>Create account</button></div>
      <form onSubmit={sendOtp}>
        <label className="auth-field">Mobile number<input aria-label="Mobile number" value={mobile} onChange={(event) => setMobile(event.target.value)} placeholder="+968 9123 4567" autoComplete="tel" /></label>
        {purpose === "registration" && <label className="auth-field">Full name<input aria-label="Full name" value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Enter your full name" autoComplete="name" /></label>}
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="primary-button auth-submit" disabled={busy} type="submit">{busy ? "Sending…" : "Send OTP"}</button>
      </form>
    </> : <>
      <button className="auth-back" type="button" onClick={() => { setChallengeId(""); setCode(""); setError(""); }}>← Back</button>
      <div className="auth-heading"><h1>Check your OTP</h1><p>We sent a verification code to <strong>{mobile}</strong>.</p></div>
      <form onSubmit={verifyOtp}>
        <label className="auth-field">Verification code<input aria-label="Verification code" value={code} onChange={(event) => setCode(event.target.value)} inputMode="numeric" autoComplete="one-time-code" placeholder="Enter the code" /></label>
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="primary-button auth-submit" disabled={busy} type="submit">{busy ? "Verifying…" : "Verify and continue"}</button>
        <button className="auth-change" type="button" onClick={() => { setChallengeId(""); setCode(""); setError(""); }}>Change mobile number</button>
      </form>
    </>}
  </section></main>;
}
function errorMessage(error: unknown): string { return error instanceof Error ? error.message : "Unable to authenticate."; }
