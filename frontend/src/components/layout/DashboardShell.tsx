"use client";

import Sidebar from "./Sidebar";
import Header from "./Header";
import AdBanner from "../dashboard/AdBanner";

type Props = {
  children: React.ReactNode;
};

export default function DashboardShell({ children }: Props) {
  return (
    <div className="flex min-h-screen w-full bg-[#06090d] text-white">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <Header />

        <main className="flex-1 overflow-x-hidden p-3 sm:p-4 md:p-6">
          <div className="mx-auto w-full max-w-[1600px] space-y-5">
            <AdBanner />
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
