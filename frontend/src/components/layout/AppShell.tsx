"use client";

import { usePathname } from "next/navigation";
import Sidebar from "./Sidebar";
import MobileBottomNav from "./MobileBottomNav";

const publicPaths = new Set(["/", "/login"]);

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isPublic = publicPaths.has(pathname);

  if (isPublic) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-[#080d12] text-white">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[240px] lg:block">
        <Sidebar />
      </aside>

      <main className="min-w-0 lg:ml-[240px] pb-16 lg:pb-0">
        {children}
      </main>

      <MobileBottomNav />
    </div>
  );
}
