import { ClipboardEvent, KeyboardEvent, useRef } from "react";

const OTP_LENGTH = 6;

interface Props {
  value: string[];
  disabled: boolean;
  onChange: (value: string[]) => void;
  onComplete: (code: string) => void;
}

export function OtpCodeInput({ value, disabled, onChange, onComplete }: Props) {
  const inputs = useRef<Array<HTMLInputElement | null>>([]);

  const updateDigit = (index: number, rawValue: string) => {
    const digit = rawValue.replace(/\D/g, "").slice(-1);
    const next = [...value];
    next[index] = digit;
    onChange(next);
    if (digit && index < OTP_LENGTH - 1) inputs.current[index + 1]?.focus();
    if (digit && next.every(Boolean)) onComplete(next.join(""));
  };

  const handleKeyDown = (index: number, event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Backspace" && !value[index] && index > 0) {
      inputs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (event: ClipboardEvent<HTMLDivElement>) => {
    event.preventDefault();
    const pasted = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, OTP_LENGTH);
    if (!pasted) return;
    const next = Array<string>(OTP_LENGTH).fill("");
    pasted.split("").forEach((digit, index) => { next[index] = digit; });
    onChange(next);
    inputs.current[Math.min(pasted.length, OTP_LENGTH) - 1]?.focus();
    if (pasted.length === OTP_LENGTH) onComplete(pasted);
  };

  return <fieldset className="otp-fieldset" disabled={disabled}>
    <legend>Enter the code</legend>
    <div className="otp-inputs" onPaste={handlePaste}>
      {value.map((digit, index) => <input
        key={index}
        ref={(element) => { inputs.current[index] = element; }}
        aria-label={`OTP digit ${index + 1}`}
        value={digit}
        onChange={(event) => updateDigit(index, event.target.value)}
        onKeyDown={(event) => handleKeyDown(index, event)}
        inputMode="numeric"
        autoComplete={index === 0 ? "one-time-code" : "off"}
        maxLength={1}
      />)}
    </div>
  </fieldset>;
}

export function emptyOtpCode(): string[] {
  return Array<string>(OTP_LENGTH).fill("");
}
