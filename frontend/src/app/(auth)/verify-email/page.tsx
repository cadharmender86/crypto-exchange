"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import {
  verifyEmail,
  resendEmailOtp,
} from "@/services/emailOtp.service";

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const email = searchParams.get("email") ?? "";

  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [countdown, setCountdown] = useState(60);

  useEffect(() => {
    if (!email) {
      router.replace("/register");
    }
  }, [email, router]);

  useEffect(() => {
    if (countdown <= 0) return;

    const timer = setTimeout(() => {
      setCountdown((prev) => prev - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [countdown]);

  const handleVerify = async () => {
    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response = await verifyEmail({
        email,
        otp,
      });

      setMessage(response.message);

      setTimeout(() => {
        router.push("/dashboard");
      }, 1500);

    } catch (err: any) {
      setError(err.message || "Verification failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    setError("");
    setMessage("");

    try {
      const response = await resendEmailOtp({
        email,
      });

      setMessage(response.message);
      setCountdown(60);

    } catch (err: any) {
      setError(err.message || "Unable to resend OTP.");
    } finally {
      setResending(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-black px-6 text-white">
      <div className="w-full max-w-md rounded-2xl border border-zinc-800 bg-zinc-950 p-8">

        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold">
            Verify Your Email
          </h1>

          <p className="mt-3 text-sm text-zinc-400">
            Enter the 6-digit verification code sent to
          </p>

          <p className="mt-1 font-medium text-emerald-400">
            {email}
          </p>
        </div>

        {/* OTP Input */}
        <label className="mb-2 block text-sm font-medium">
          Verification Code <span className="text-red-500">*</span>
        </label>

        <input
          type="text"
          value={otp}
          onChange={(e) =>
            setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
          }
          maxLength={6}
          placeholder="Enter 6-digit OTP"
          className="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-3 text-center text-2xl tracking-[0.5em] outline-none focus:border-emerald-500"
        />

        {message && (
          <div className="mt-5 rounded-lg border border-emerald-700 bg-emerald-900/20 p-3 text-sm text-emerald-400">
            {message}
          </div>
        )}

        {error && (
          <div className="mt-5 rounded-lg border border-red-700 bg-red-900/20 p-3 text-sm text-red-400">
            {error}
          </div>
        )}

        <button
          onClick={handleVerify}
          disabled={loading || otp.length !== 6}
          className="mt-6 w-full rounded-lg bg-emerald-600 py-3 font-semibold hover:bg-emerald-500 disabled:bg-zinc-700"
        >
          {loading ? "Verifying..." : "Verify Email"}
        </button>

        <div className="mt-6 text-center text-sm text-zinc-400">

          Didn't receive the code?

          {countdown > 0 ? (
            <p className="mt-2 text-zinc-500">
              Resend in {countdown}s
            </p>
          ) : (
            <button
              onClick={handleResend}
              disabled={resending}
              className="mt-2 text-emerald-400 hover:underline"
            >
              {resending ? "Sending..." : "Resend OTP"}
            </button>
          )}

        </div>

      </div>
    </main>
  );
}