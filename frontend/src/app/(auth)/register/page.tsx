"use client";

import { SubmitEvent, useState } from "react";
// import Link from "next/link";
import { Eye, EyeOff } from "lucide-react";
import { useRouter } from "next/navigation";
import { registerUser } from "@/services/auth.service";

export default function RegisterPage() {
  const router = useRouter();

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    mobile: "",
    password: "",
    confirm_password: "",
    referral_code: "",
    accept_terms: false,
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const { name, value, type, checked } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const isFormValid =
    form.first_name.trim() !== "" &&
    form.last_name.trim() !== "" &&
    form.email.trim() !== "" &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) &&
    form.mobile.trim().length === 10 &&
    form.password.length >= 8 &&
    form.confirm_password === form.password &&
    form.accept_terms;

  const handleSubmit = async (e: SubmitEvent) => {
    e.preventDefault();

    setError("");

    if (form.password !== form.confirm_password) {
        setError("Passwords do not match.");
        return;
    }

    if (!isFormValid) {
      setError("Please complete all required fields correctly.");
      return;
    }

    if (!form.accept_terms) {
        setError("Please accept Terms & Privacy Policy.");
        return;
    }

    setLoading(true);

    try {
        await registerUser({
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        mobile: form.mobile,
        password: form.password,
        referral_code: form.referral_code || undefined,
        });

        router.push(
            `/verify-email?email=${encodeURIComponent(form.email)}`,
        );
    } catch (err: any) {
        setError(err.message || "Registration failed.");
    } finally {
        setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-black text-white flex items-center justify-center p-6">
      <div className="w-full max-w-xl rounded-2xl border border-zinc-800 bg-zinc-950 p-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold">Create BitNova Account</h1>
          <p className="mt-2 text-zinc-400">
            Start trading crypto securely.
          </p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-2 block text-sm font-medium text-zinc-300">
                First Name <span className="text-red-500">*</span>
              </label>

              <input
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-3"
                placeholder="Enter first name"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-zinc-300">
                Last Name <span className="text-red-500">*</span>
              </label>
            
              <input
                name="last_name"                
                value={form.last_name}
                onChange={handleChange}
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-3"
                placeholder="Enter last name"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-zinc-300">
                Email <span className="text-red-500">*</span>
              </label>

              <input
                name="email"                
                type="email"
                value={form.email}
                onChange={handleChange}
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 p-3"
                placeholder="Email Address"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-zinc-300">
                Mobile Number <span className="text-red-500">*</span>
              </label>
          
              <div className="flex rounded-lg border border-zinc-700 overflow-hidden bg-zinc-900">
                <span className="px-4 flex items-center text-zinc-400 border-r border-zinc-700">
                  +91
                </span>

                <input
                  name="mobile"
                  placeholder="Mobile Number"
                  value={form.mobile}
                  onChange={handleChange}
                  className="w-full bg-transparent p-3 outline-none"
                />
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-zinc-300">
                Password <span className="text-red-500">*</span>
              </label>
          
              <div className="relative">
                <input
                  name="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Password"
                  value={form.password}
                  onChange={handleChange}
                  className="w-full rounded-lg bg-zinc-900 border border-zinc-700 p-3 pr-12"
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-zinc-400"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-zinc-300">
                Confirm Password <span className="text-red-500">*</span>
              </label>
          
              <div className="relative">
                <input
                  name="confirm_password"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Confirm Password"
                  value={form.confirm_password}
                  onChange={handleChange}
                  className="w-full rounded-lg bg-zinc-900 border border-zinc-700 p-3 pr-12"
                />

                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-3 text-zinc-400"
                >
                  {showConfirmPassword ? (
                    <EyeOff size={20} />
                  ) : (
                    <Eye size={20} />
                  )}
                </button>
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-zinc-300">
                Referal Code
              </label>
                    
              <input
                name="referral_code"
                placeholder="Referral Code (Optional)"
                value={form.referral_code}
                onChange={handleChange}
                className="w-full rounded-lg bg-zinc-900 border border-zinc-700 p-3"
              />
            </div>
          </div>

          <label className="flex items-start gap-3 text-sm text-zinc-400">
            <input
              type="checkbox"
              name="accept_terms"
              checked={form.accept_terms}
              onChange={handleChange}
              className="mt-1"
            />

            <span>
              <span className="text-red-500">*</span>
              I agree to BitNova Terms of Service and Privacy Policy.
            </span>
          </label>

          {error && (
            <div className="rounded-lg border border-red-700 bg-red-900/20 p-3 text-sm text-red-400">
                {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !isFormValid}
            className={`w-full rounded-lg py-3 font-semibold transition ${
              loading || !isFormValid
                ? "cursor-not-allowed bg-zinc-700 text-zinc-400"
                : "bg-emerald-600 text-white hover:bg-emerald-500"
            }`}
          >
            {loading ? "Creating Account..." : "Create Account"}
          </button>
        </form>

        {/* <div className="mt-6 text-center text-sm text-zinc-400">
            Don't have an account?{" "}

            <Link
                href="/register"
                className="font-medium text-emerald-400 hover:text-emerald-300 hover:underline"
            >
                Create Account
            </Link> */}

        <div className="mt-8 text-center text-sm text-zinc-400">
          Already have an account?

          <button
            onClick={() => router.push("/login")}
            className="ml-2 text-emerald-400 hover:underline"
          >
            Sign In
          </button>
        </div>
      </div>
    </main>
  );
}