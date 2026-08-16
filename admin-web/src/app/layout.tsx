import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "BitNova Admin",
  description: "BitNova exchange administration portal",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
