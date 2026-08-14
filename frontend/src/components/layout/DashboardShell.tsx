"use client";

import Sidebar from "./Sidebar";
import Header from "./Header";

type Props = {
  children: React.ReactNode;
};

export default function DashboardShell({ children }: Props) {
  return (
    <div className="flex min-h-screen bg-[#06090d] text-white">
      <Sidebar />

      <div className="flex flex-1 flex-col">
        <Header />

        <main className="w-full flex-1 overflow-x-hidden p-4 md:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
