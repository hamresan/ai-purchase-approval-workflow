import { FormEvent, KeyboardEvent, useRef, useState } from "react";
import type { AuthPurpose, IdentityAuthApi } from "@/auth/api";
import type { AuthSession } from "@/auth/session";

const OTP_LENGTH = 6;

interface Props { api: IdentityAuthApi; onAuthenticated: (session: AuthSession) => void; }

export function AuthScreen({ api, onAuthenticated }: Props) {
  const [purpose, setPurpose] = useState<AuthPurpose>("login");
  const [challengeId, setChallengeId] = useState("");
  const [mobile, setMobile] = useState("");
  const [fullName, setFullName] = useState("");
  const [digits, setDigits] = useState(() => Array<string>(OTP_LENGTH).fill(""));
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const otpInputs = useRef<Array<HTMLInputElement | null>>([]);

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

  const verifyCode = async (code: string) => {
    if (code.length !== OTP_LENGTH || busy) return;
    setBusy(true); setError("");
    try {
      onAuthenticated(await api.verifyOtp(challengeId, code, purpose === "registration" ? fullName.trim() : undefined));
    } catch (caught) { setError(errorMessage(caught)); } finally { setBusy(false); }
  };

  const verifyOtp = async (event: FormEvent) => {
    event.preventDefault();
    const code = digits.join("");
    if (code.length !== OTP_LENGTH) return setError("Enter the 6-digit verification code.");
    await verifyCode(code);
  };

  const updateDigit = (index: number, value: string) => {
    const digit = value.replace(/\D/g, "").slice(-1);
    const next = [...digits];
    next[index] = digit;
    setDigits(next);
    setError("");
    if (digit && index < OTP_LENGTH - 1) otpInputs.current[index + 1]?.focus();
    if (digit && index === OTP_LENGTH - 1 && next.every(Boolean)) void verifyCode(next.join(""));
  };

  const handleOtpKeyDown = (index: number, event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Backspace" && !digits[index] && index > 0) otpInputs.current[index - 1]?.focus();
  };

  const handleOtpPaste = (value: string) => {
    const pasted = value.replace(/\D/g, "").slice(0, OTP_LENGTH);
    if (!pasted) return;
    const next = Array<string>(OTP_LENGTH).fill("");
    pasted.split("").forEach((digit, index) => { next[index] = digit; });
    setDigits(next);
    setError("");
    otpInputs.current[Math.min(pasted.length, OTP_LENGTH) - 1]?.focus();
    if (pasted.length === OTP_LENGTH) void verifyCode(pasted);
  };

  const resetOtp = () => { setChallengeId(""); setDigits(Array<string>(OTP_LENGTH).fill("")); setError(""); };

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
      <button className="auth-back" type="button" onClick={resetOtp}>← Back</button>
      <div className="auth-heading"><h1>Check your OTP</h1><p>We sent a verification code to <strong>{mobile}</strong>.</p></div>
      <form onSubmit={verifyOtp}>
        <fieldset className="otp-fieldset" disabled={busy}>
          <legend>Enter the code</legend>
          <div className="otp-inputs" onPaste={(event) => { event.preventDefault(); handleOtpPaste(event.clipboardData.getData("text")); }}>
            {digits.map((digit, index) => <input key={index} ref={(element) => { otpInputs.current[index] = element; }} aria-label={`OTP digit ${index + 1}`} value={digit} onChange={(event) => updateDigit(index, event.target.value)} onKeyDown={(event) => handleOtpKeyDown(index, event)} inputMode="numeric" autoComplete={index === 0 ? "one-time-code" : "off"} maxLength={1} />)}
          </div>
        </fieldset>
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="primary-button auth-submit" disabled={busy} type="submit">{busy ? "Verifying…" : "Verify and continue"}</button>
        <button className="auth-change" type="button" onClick={resetOtp}>Change mobile number</button>
      </form>
    </>}
  </section></main>;
}
function errorMessage(error: unknown): string { return error instanceof Error ? error.message : "Unable to authenticate."; }
