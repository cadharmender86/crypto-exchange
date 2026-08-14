"use client";

import { ReactNode, useState } from "react";

type AccordionSectionProps = {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
};

export default function AccordionSection({
  title,
  children,
  defaultOpen = false,
}: AccordionSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section className="rounded-xl border border-gray-800 bg-[#111318]">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between px-6 py-4 text-left"
      >
        <span className="font-semibold text-white">{title}</span>
        <span className="text-gray-400">
          {open ? "−" : "+"}
        </span>
      </button>

      {open && (
        <div className="border-t border-gray-800 px-6 py-5">
          {children}
        </div>
      )}
    </section>
  );
}
