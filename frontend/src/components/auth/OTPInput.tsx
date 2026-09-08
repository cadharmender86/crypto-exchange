"use client";

import { useRef } from "react";

type OTPInputProps = {
  value: string;
  onChange: (value: string) => void;
};

export default function OTPInput({
  value,
  onChange,
}: OTPInputProps) {
  const inputs = useRef<(HTMLInputElement | null)[]>([]);

  const digits = value.padEnd(6, " ").slice(0, 6).split("");

  const updateDigit = (digit: string, index: number) => {
    const values = value.padEnd(6, " ").slice(0, 6).split("");
    values[index] = digit;
    onChange(values.join("").trimEnd());

    if (digit && index < 5) {
      inputs.current[index + 1]?.focus();
    }
  };

  return (
    <div className="flex justify-between gap-2">
      {digits.map((digit, index) => (
        <input
          key={index}
          ref={(el) => {
            inputs.current[index] = el;
          }}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={digit === " " ? "" : digit}
          onChange={(e) => {
            const val = e.target.value.replace(/\\D/g, "");
            updateDigit(val, index);
          }}
          onKeyDown={(e) => {
            if (
              e.key === "Backspace" &&
              !digits[index] &&
              index > 0
            ) {
              inputs.current[index - 1]?.focus();
            }
          }}
          className="h-14 w-12 rounded-xl border border-zinc-700 bg-zinc-900 text-center text-xl font-bold text-white outline-none focus:border-emerald-500"
        />
      ))}
    </div>
  );
}