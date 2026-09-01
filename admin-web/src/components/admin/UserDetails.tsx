"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { adminFetch } from "@/lib/adminApi";

/* -------------------------------------------------------------------------- */
/*                                   TYPES                                    */
/* -------------------------------------------------------------------------- */

type UserBalance = {
  asset_symbol: string;
  available_balance: string;
  locked_balance: string;
};

type UserBankAccount = {
  id: string;
  account_holder_name: string;
  bank_name: string;
  account_number: string;
  ifsc_code: string;

  account_type: string;
  status: string;
  is_primary: boolean;
  verified_at: string | null;
};

type UserKYC = {
  status: string;
  full_name: string | null;
  pan_number: string | null;
  aadhaar_number: string | null;
  reviewed_at: string | null;
};

type Deposit = {
  id: string;
  deposit_type: "FIAT" | "CRYPTO";
  asset_symbol: string;
  network: string | null;
  amount: string;
  status: string;
  blockchain_tx_hash: string | null;
  confirmations: number;
  created_at: string;
};

type Withdrawal = {
  id: string;
  withdrawal_type: "FIAT" | "CRYPTO";
  asset_symbol: string;
  network: string | null;
  amount: string;
  status: string;
  destination_address: string | null;
  created_at: string;
};

type AuditLog = {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  result: string;
  reason: string | null;
  created_at: string;
};

type User = {
  id: string;
  email: string;

  is_active: boolean;
  is_verified: boolean;
  two_factor_enabled: boolean;
  
  last_login_at: string | null;
  created_at: string;
  updated_at: string;

  balances: UserBalance[];
  bank_accounts: UserBankAccount[];
  kyc: UserKYC | null;

  recent_deposits: Deposit[];
  recent_withdrawals: Withdrawal[];

   // NEW FIELDS
  deposit_count: number;
  withdrawal_count: number;

  transaction_summary: {
    deposits: number;
    withdrawals: number;
  };
};

/* -------------------------------------------------------------------------- */
/*                                  HELPERS                                   */
/* -------------------------------------------------------------------------- */

function formatDate(value: string | null) {
  if (!value) return "Never";
  return new Date(value).toLocaleString();
}

function shortId(value?: string | null) {
  if (!value) return "—";
  return value.length > 18
    ? `${value.slice(0, 10)}...${value.slice(-6)}`
    : value;
}

/* -------------------------------------------------------------------------- */
/*                              STATUS COMPONENT                              */
/* -------------------------------------------------------------------------- */

function StatusBadge({ value }: { value: string }) {
  const status = value.toUpperCase();

  let classes =
    "rounded-full px-2 py-1 text-xs font-medium bg-slate-700/40 text-slate-300";

  if (
    ["APPROVED", "SUCCESS", "COMPLETED", "CONFIRMED", "ACTIVE"].includes(status)
  ) {
    classes =
      "rounded-full px-2 py-1 text-xs font-medium bg-emerald-500/10 text-emerald-300";
  }

  if (["PENDING", "UNDER_REVIEW", "PROCESSING"].includes(status)) {
    classes =
      "rounded-full px-2 py-1 text-xs font-medium bg-yellow-500/10 text-yellow-300";
  }

  if (["REJECTED", "FAILED", "FROZEN"].includes(status)) {
    classes =
      "rounded-full px-2 py-1 text-xs font-medium bg-red-500/10 text-red-300";
  }

  return <span className={classes}>{value}</span>;
}

/* -------------------------------------------------------------------------- */
/*                               MAIN COMPONENT                               */
/* -------------------------------------------------------------------------- */

export default function UserDetails({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await adminFetch(`/api/v1/admin/users/${userId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to load user.");
      }

      setUser(data);

      /* Optional audit logs */
      try {
        const auditResponse = await adminFetch(
          `/api/v1/admin/audit-logs?limit=20&resource_type=USER&resource_id=${userId}`
        );

        if (auditResponse.ok) {
          const auditData = await auditResponse.json();

          setLogs(
            auditData
              .filter(
                (log: AuditLog) =>
                  log.resource_type === "USER" &&
                  log.resource_id === userId
              )
              .slice(0, 10)
          );
        }
      } catch {
        // ignore permission error
      }
    } catch (err) {
      if (err instanceof Error) setError(err.message);
      else setError("Unable to load user.");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    load();
  }, [load]);

  const toggleUserStatus = async () => {
    if (!user) return;

    setActionLoading(true);
    setError("");
    setNotice("");

    try {
      // Backend endpoints
      const endpoint = user.is_active ? "freeze" : "unfreeze";

      const response = await adminFetch(
        `/api/v1/admin/users/${user.id}/${endpoint}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to update user status");
      }

      setNotice(data.message ?? "User status updated.");

      // Reload latest user data
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-10 text-center text-slate-400">
        Loading user...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="rounded-xl bg-red-900/20 border border-red-700 p-6 text-red-300">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">

      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <Link
          href="/admin/users"
          className="text-sm text-cyan-400 hover:text-cyan-300"
        >
          ← Back to Users
        </Link>

        <div className="mt-5 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">{user.email}</h1>

            <p className="mt-2 text-xs text-slate-500">
              User ID: {shortId(user.id)}
            </p>
          </div>

          <button
            onClick={toggleUserStatus}
            disabled={actionLoading}
            className={`rounded-lg px-4 py-2 text-sm font-medium text-white ${
              user.is_active ? "bg-red-600" : "bg-emerald-600"
            }`}
          >
            {actionLoading
              ? "Processing..."
              : user.is_active
              ? "Freeze User"
              : "Unfreeze User"}
          </button>
        </div>
      </div>

      {notice && (
        <div className="rounded-xl bg-emerald-900/20 border border-emerald-700 p-3 text-emerald-300">
          {notice}
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-900/20 border border-red-700 p-3 text-red-300">
          {error}
        </div>
      )}

            {/* ================= ACCOUNT STATUS ================= */}

      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <h2 className="mb-5 text-lg font-semibold text-white">Account Status</h2>

        <div className="grid gap-4 md:grid-cols-2">
          <InfoRow
            label="Account Status"
            value={
              user.is_active ? (
                <StatusBadge value="ACTIVE" />
              ) : (
                <StatusBadge value="FROZEN" />
              )
            }
          />

          <InfoRow
            label="Email Verified"
            value={
              user.is_verified ? (
                <StatusBadge value="APPROVED" />
              ) : (
                <StatusBadge value="PENDING" />
              )
            }
          />

          <InfoRow
            label="Two Factor Authentication"
            value={user.two_factor_enabled ? "Enabled" : "Disabled"}
          />

          <InfoRow
            label="Last Login"
            value={formatDate(user.last_login_at)}
          />

          <InfoRow
            label="Created At"
            value={formatDate(user.created_at)}
          />

          <InfoRow
            label="Updated At"
            value={formatDate(user.updated_at)}
          />
        </div>
      </div>

      {/* ================= WALLET BALANCES ================= */}

      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Wallet Balances
          </h2>

          <span className="text-xs text-slate-500">
            {user.balances.length} Assets
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b border-slate-700 text-slate-400">
              <tr>
                <th className="pb-3 text-left">Asset</th>
                <th className="pb-3 text-right">Available</th>
                <th className="pb-3 text-right">Locked</th>
              </tr>
            </thead>

            <tbody>
              {user.balances.length === 0 ? (
                <tr>
                  <td
                    colSpan={3}
                    className="py-6 text-center text-slate-500"
                  >
                    No balances available.
                  </td>
                </tr>
              ) : (
                user.balances.map((balance) => (
                  <tr
                    key={balance.asset_symbol}
                    className="border-b border-slate-800"
                  >
                    <td className="py-4 font-medium text-white">
                      {balance.asset_symbol}
                    </td>

                    <td className="py-4 text-right text-emerald-400">
                      {balance.available_balance}
                    </td>

                    <td className="py-4 text-right text-yellow-400">
                      {balance.locked_balance}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ================= BANK ACCOUNTS ================= */}

      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Linked Bank Accounts
          </h2>

          <span className="text-xs text-slate-500">
            {user.bank_accounts.length} Accounts
          </span>
        </div>

        {user.bank_accounts.length === 0 ? (
          <p className="text-sm text-slate-500">
            No bank account linked with this user.
          </p>
        ) : (
          <div className="space-y-4">
            {user.bank_accounts.map((bank) => (
              <div
                key={bank.id}
                className="rounded-xl border border-slate-700 bg-slate-900/40 p-5"
              >
                <div className="mb-3 flex items-center justify-between">
                  <div className="font-medium text-white">
                    {bank.account_holder_name}
                  </div>

                  <StatusBadge
                    value={bank.status}
                  />
                  <InfoRow label="Account Type" value={bank.account_type} />
                  <InfoRow
                    label="Primary Account"
                    value={bank.is_primary ? "Yes" : "No"}
                  />
                  <InfoRow
                    label="Verified At"
                    value={bank.verified_at ? formatDate(bank.verified_at) : "Not Verified"}
                  />  
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <InfoRow label="Bank" value={bank.bank_name} />
                  <InfoRow label="IFSC Code" value={bank.ifsc_code} />
                  <InfoRow
                    label="Account Number"
                    value={bank.account_number}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ===================== KYC DETAILS ===================== */}

      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <h2 className="mb-5 text-lg font-semibold text-white">
          KYC Details
        </h2>

        {!user.kyc ? (
          <p className="text-sm text-slate-500">
            User has not submitted KYC.
          </p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            <InfoRow
              label="KYC Status"
              value={<StatusBadge value={user.kyc.status} />}
            />

            <InfoRow
              label="Reviewed At"
              value={formatDate(user.kyc.reviewed_at)}
            />

            <InfoRow
              label="Full Name"
              value={user.kyc.full_name ?? "—"}
            />

            <InfoRow
              label="PAN Number"
              value={user.kyc.pan_number ?? "—"}
            />

            <InfoRow
              label="Aadhaar Number"
              value={user.kyc.aadhaar_number ?? "—"}
            />
          </div>
        )}
      </div>

      {/* ================= TRANSACTION SUMMARY ================= */}

      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <h2 className="mb-5 text-lg font-semibold text-white">
          Transaction Summary
        </h2>

        <div className="grid gap-5 md:grid-cols-2">
          <SummaryCard
            title="Total Deposits"
            value={user.deposit_count}
            color="text-emerald-400"
          />

          <SummaryCard
            title="Total Withdrawals"
            value={user.withdrawal_count}
            color="text-orange-400"
          />
        </div>
      </div>

          {/* ================= RECENT DEPOSITS ================= */}

      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Recent Deposits
          </h2>

          <span className="text-xs text-slate-500">
            {user.recent_deposits.length} Records
          </span>
        </div>

        <TransactionTable
          type="deposit"
          rows={user.recent_deposits}
        />
      </div>

      {/* ================= RECENT WITHDRAWALS ================= */}

      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Recent Withdrawals
          </h2>

          <span className="text-xs text-slate-500">
            {user.recent_withdrawals.length} Records
          </span>
        </div>

        <TransactionTable
          type="withdrawal"
          rows={user.recent_withdrawals}
        />
      </div>

      {/* ================= AUDIT LOGS ================= */}

      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Recent Audit Activity
          </h2>

          <span className="text-xs text-slate-500">
            {logs.length} Events
          </span>
        </div>

        {logs.length === 0 ? (
          <p className="text-sm text-slate-500">
            No audit records available for this user.
          </p>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => (
              <div
                key={log.id}
                className="rounded-xl border border-slate-700 bg-slate-900/40 p-4"
              >
                <div className="flex items-center justify-between">
                  <p className="font-medium text-white">
                    {log.action}
                  </p>

                  <StatusBadge value={log.result} />
                </div>

                <p className="mt-1 text-xs text-slate-500">
                  {formatDate(log.created_at)}
                </p>

                {log.reason && (
                  <p className="mt-3 text-sm text-slate-300">
                    {log.reason}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*                            REUSABLE COMPONENTS                             */
/* -------------------------------------------------------------------------- */

function InfoRow({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900/30 p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <div className="mt-2 text-sm text-white">
        {value}
      </div>
    </div>
  );
}

function SummaryCard({
  title,
  value,
  color,
}: {
  title: string;
  value: number;
  color: string;
}) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/40 p-6">
      <p className="text-sm text-slate-400">{title}</p>

      <p className={`mt-3 text-3xl font-bold ${color}`}>
        {value}
      </p>
    </div>
  );
}


function TransactionStatus({ value }: { value: string }) {
  const normalized = value.toUpperCase();

  let classes =
    "rounded-full px-2 py-1 text-xs font-medium ";

  if (["APPROVED", "COMPLETED", "CONFIRMED", "SUCCESS"].includes(normalized)) {
    classes += "bg-emerald-500/20 text-emerald-300";
  } else if (
    ["PENDING", "PROCESSING", "UNDER_REVIEW"].includes(normalized)
  ) {
    classes += "bg-amber-500/20 text-amber-300";
  } else if (["REJECTED", "FAILED", "CANCELLED"].includes(normalized)) {
    classes += "bg-red-500/20 text-red-300";
  } else {
    classes += "bg-slate-700/40 text-slate-300";
  }

  return <span className={classes}>{value}</span>;
}

/* -------------------------------------------------------------------------- */
/*                           TRANSACTION TABLE                                */
/* -------------------------------------------------------------------------- */

function TransactionTable({
  type,
  rows,
}: {
  type: "deposit" | "withdrawal";
  rows: Deposit[] | Withdrawal[];
}) {
  const isDeposit = type === "deposit";

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="border-b border-slate-800 text-slate-400">
          <tr>
            <th className="px-4 py-3 text-left">Date</th>
            <th className="px-4 py-3 text-left">Type</th>
            <th className="px-4 py-3 text-left">Asset</th>
            <th className="px-4 py-3 text-left">Network</th>
            <th className="px-4 py-3 text-right">Amount</th>

            {isDeposit ? (
              <th className="px-4 py-3 text-center">Confirmations</th>
            ) : (
              <th className="px-4 py-3 text-left">Destination</th>
            )}

            <th className="px-4 py-3 text-center">Status</th>
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-800">
          {rows.length === 0 ? (
            <tr>
              <td colSpan={7} className="px-4 py-6 text-center text-slate-500">
                No recent {type}s found.
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={row.id} className="hover:bg-slate-900/40">
                <td className="px-4 py-3 text-slate-300">
                  {formatDate(row.created_at)}
                </td>

                <td className="px-4 py-3">
                  {(() => {
                    const transactionType =
                      "deposit_type" in row ? row.deposit_type : row.withdrawal_type;

                    const isCrypto = transactionType === "CRYPTO";

                    return (
                      <span
                        className={
                          isCrypto
                            ? "rounded bg-cyan-500/20 px-2 py-1 text-xs text-cyan-300"
                            : "rounded bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300"
                        }
                      >
                        {transactionType}
                      </span>
                    );
                  })()}
                </td>

                <td className="px-4 py-3 font-medium text-white">
                  {row.asset_symbol}
                </td>

                <td className="px-4 py-3 text-slate-300">
                  {row.network ?? "INR"}
                </td>

                <td className="px-4 py-3 text-right font-medium text-white">
                  {row.amount}
                </td>

                {isDeposit ? (
                  <td className="px-4 py-3 text-center text-slate-300">
                    {"confirmations" in row ? row.confirmations : "-"}
                  </td>
                ) : (
                  <td className="px-4 py-3 text-slate-300">
                    {"destination_address" in row
                      ? shortId(row.destination_address)
                      : "-"}
                  </td>
                )}

                <td className="px-4 py-3 text-center">
                  <TransactionStatus value={row.status} />
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}