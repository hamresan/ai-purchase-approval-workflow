import { FormEvent, useState } from "react";
import type { AuthPurpose, IdentityAuthApi } from "@/auth/api";
import type { AuthSession } from "@/auth/session";
import { emptyOtpCode, OtpCodeInput } from "@/features/auth/OtpCodeInput";

interface Props { api: IdentityAuthApi; onAuthenticated: (session: AuthSession) => void; }

type AuthStep = "mobile" | "otp" | "profile";

export function AuthScreen({ api, onAuthenticated }: Props) {
  const [purpose, setPurpose] = useState<AuthPurpose>("login");
  const [step, setStep] = useState<AuthStep>("mobile");
  const [challengeId, setChallengeId] = useState("");
  const [mobile, setMobile] = useState("");
  const [fullName, setFullName] = useState("");
  const [digits, setDigits] = useState(emptyOtpCode);
  const [verifiedSession, setVerifiedSession] = useState<AuthSession | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const sendOtp = async (event: FormEvent) => {
    event.preventDefault();
    if (!mobile.trim()) return setError("Enter your mobile number.");
    setBusy(true); setError("");
    try {
      const challenge = await api.requestOtp(mobile.trim(), purpose);
      setChallengeId(challenge.challengeId);
      setStep("otp");
    } catch (caught) { setError(errorMessage(caught)); } finally { setBusy(false); }
  };

  const verifyCode = async (code: string) => {
    if (code.length !== 6 || busy) return;
    setBusy(true); setError("");
    try {
      const session = await api.verifyOtp(challengeId, code, purpose === "registration" ? "New user" : undefined);
      if (purpose === "registration") {
        setVerifiedSession(session);
        setStep("profile");
      } else {
        onAuthenticated(session);
      }
    } catch (caught) { setError(errorMessage(caught)); } finally { setBusy(false); }
  };

  const verifyOtp = async (event: FormEvent) => {
    event.preventDefault();
    const code = digits.join("");
    if (code.length !== 6) return setError("Enter the 6-digit verification code.");
    await verifyCode(code);
  };

  const completeProfile = async (event: FormEvent) => {
    event.preventDefault();
    if (!fullName.trim()) return setError("Enter your full name.");
    if (!verifiedSession) return setError("Registration session is unavailable.");
    setBusy(true); setError("");
    try {
      await api.updateProfile(verifiedSession.accessToken, fullName.trim());
      onAuthenticated(verifiedSession);
    } catch (caught) { setError(errorMessage(caught)); } finally { setBusy(false); }
  };

  const resetMobile = () => {
    setStep("mobile"); setChallengeId(""); setDigits(emptyOtpCode()); setVerifiedSession(null); setError("");
  };

  return <main className="auth-page"><section className="auth-card">
    <header className="auth-brand"><span className="brand-mark">🛒</span><strong>Purchase Requests</strong></header>
    {step === "mobile" && <>
      <div className="auth-heading"><h1>{purpose === "login" ? "Welcome back" : "Create your account"}</h1><p>Use your mobile number to continue securely with a one-time code.</p></div>
      <div className="auth-mode"><button type="button" className={purpose === "login" ? "active" : ""} onClick={() => setPurpose("login")}>Sign in</button><button type="button" className={purpose === "registration" ? "active" : ""} onClick={() => setPurpose("registration")}>Create account</button></div>
      <form onSubmit={sendOtp}>
        <label className="auth-field">Mobile number<input aria-label="Mobile number" value={mobile} onChange={(event) => setMobile(event.target.value)} placeholder="+968 9123 4567" autoComplete="tel" /></label>
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="primary-button auth-submit" disabled={busy} type="submit">{busy ? "Sending…" : "Send OTP"}</button>
      </form>
    </>}
    {step === "otp" && <>
      <button className="auth-back" type="button" onClick={resetMobile}>← Back</button>
      <div className="auth-heading"><h1>Check your OTP</h1><p>We sent a verification code to <strong>{mobile}</strong>.</p></div>
      <form onSubmit={verifyOtp}>
        <OtpCodeInput value={digits} disabled={busy} onChange={(value) => { setDigits(value); setError(""); }} onComplete={(code) => void verifyCode(code)} />
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="primary-button auth-submit" disabled={busy} type="submit">{busy ? "Verifying…" : "Verify and continue"}</button>
        <button className="auth-change" type="button" onClick={resetMobile}>Change mobile number</button>
      </form>
    </>}
    {step === "profile" && <>
      <div className="auth-heading"><h1>Set up your profile</h1><p>Tell us your name to finish creating your account.</p></div>
      <form onSubmit={completeProfile}>
        <label className="auth-field">Full name<input aria-label="Full name" value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Enter your full name" autoComplete="name" /></label>
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="primary-button auth-submit" disabled={busy} type="submit">{busy ? "Saving…" : "Continue"}</button>
      </form>
    </>}
  </section></main>;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Unable to authenticate.";
}
