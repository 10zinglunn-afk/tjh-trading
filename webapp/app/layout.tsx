import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Skeptic's Machine — backtest visualizer",
  description:
    "A pretty signal is not a real edge. See strategies look good frictionless and die after costs and out-of-sample testing.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
