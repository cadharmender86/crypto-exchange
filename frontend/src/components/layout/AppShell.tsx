"use client";

import { usePathname } from "next/navigation";
import Sidebar from "./Sidebar";
// import Header from "./Header";

export default function AppShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  // Auth pages should NOT use sidebar layout
  const isAuthPage =
    pathname === "/login" ||
    pathname === "/register" ||
    pathname === "/verify-email" ||
    pathname.startsWith("/auth");

  if (isAuthPage) {
    return <>{children}</>;
  }

  console.log("Current pathname:", pathname);
  console.log("Is Auth Page:", isAuthPage);

  return (
    <div className="flex min-h-screen bg-black text-white">
      <Sidebar />

      <main className="flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  );
}