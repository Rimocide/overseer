import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Workspace Chat Engine",
  description: "Stateless AI System Interface",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning><body>
      {children}
    </body></html>
  );
}

