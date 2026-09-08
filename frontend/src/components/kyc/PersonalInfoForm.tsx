"use client";

import { useEffect, useState } from "react";
import { getKYCProfile, savePersonalInfo } from "@/services/kyc";
import { PersonalInfo } from "@/types/kyc";

const emptyForm: PersonalInfo = {
  kyc_status: "NOT_STARTED",

  first_name: "",
  last_name: "",

  date_of_birth: "",

  nationality: "",
  country: "",
  state: "",
  city: "",

  address_line1: "",
  address_line2: "",
  postal_code: "",
};

export default function PersonalInfoForm() {
  const [form, setForm] = useState(emptyForm);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState("");

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await getKYCProfile();
        setForm(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  const updateField = (key: keyof PersonalInfo, value: string) => {
    setForm((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setSuccess("");

    try {
      const updated = await savePersonalInfo({
        first_name: form.first_name,
        last_name: form.last_name,
        date_of_birth: form.date_of_birth,
        nationality: form.nationality,
        country: form.country,
        state: form.state,
        city: form.city,
        address_line1: form.address_line1,
        address_line2: form.address_line2,
        postal_code: form.postal_code,
      });

      setForm(updated);
      setSuccess("Personal information saved successfully.");
    } catch (error) {
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <section className="rounded-xl border border-slate-800 bg-[#0d141c] p-6">
        <p className="text-slate-400">Loading KYC profile...</p>
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-slate-800 bg-[#0d141c] p-6">
      <h2 className="text-xl font-semibold">Personal Information</h2>

      <p className="mt-2 text-sm text-slate-400">
        Fill your identity details exactly as per your PAN and Aadhaar.
      </p>

      {success && (
        <div className="mt-4 rounded-lg border border-green-600/30 bg-green-600/10 p-3 text-sm text-green-400">
          {success}
        </div>
      )}

      <div className="mt-6 space-y-4">

        {/* First Name */}
        <input
          value={form.first_name}
          onChange={(e) => updateField("first_name", e.target.value)}
          placeholder="First Name"
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        {/* Last Name */}
        <input
          value={form.last_name}
          onChange={(e) => updateField("last_name", e.target.value)}
          placeholder="Last Name"
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        {/* Date of Birth */}
        <input
          type="date"
          value={form.date_of_birth}
          onChange={(e) => updateField("date_of_birth", e.target.value)}
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        {/* Nationality */}
        <input
          value={form.nationality}
          onChange={(e) => updateField("nationality", e.target.value)}
          placeholder="Nationality"
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        {/* Country */}
        <input
          value={form.country}
          onChange={(e) => updateField("country", e.target.value)}
          placeholder="Country"
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        {/* State */}
        <input
          value={form.state}
          onChange={(e) => updateField("state", e.target.value)}
          placeholder="State"
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        {/* City */}
        <input
          value={form.city}
          onChange={(e) => updateField("city", e.target.value)}
          placeholder="City"
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        {/* Address */}
        <input
          value={form.address_line1}
          onChange={(e) => updateField("address_line1", e.target.value)}
          placeholder="Address Line 1"
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        <input
          value={form.address_line2}
          onChange={(e) => updateField("address_line2", e.target.value)}
          placeholder="Address Line 2 (Optional)"
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        {/* Postal Code */}
        <input
          value={form.postal_code}
          onChange={(e) => updateField("postal_code", e.target.value)}
          placeholder="Postal Code"
          className="w-full rounded-lg border border-slate-700 bg-[#131d27] px-4 py-3 text-white"
        />

        <button
          onClick={handleSave}
          disabled={saving}
          className="mt-2 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {saving ? "Saving..." : "Save Personal Information"}
        </button>

      </div>
    </section>
  );
}