import type { Metadata, Viewport } from "next";
import { DM_Sans, Sora } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

// Display font - distinctive geometric sans-serif for headings
const sora = Sora({
  subsets: ["latin"],
  variable: "--font-satoshi",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

// Body font - refined humanist sans-serif for readability
const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: {
    default: "Flowspace - Modern Task Management",
    template: "%s | Flowspace",
  },
  description:
    "Streamline your productivity with Flowspace - the intelligent task management platform for modern teams and professionals.",
  keywords: [
    "task management",
    "productivity",
    "project management",
    "team collaboration",
    "workflow",
    "todo app",
  ],
  authors: [{ name: "Flowspace Team" }],
  creator: "Flowspace",
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "Flowspace",
    title: "Flowspace - Modern Task Management",
    description: "Streamline your productivity with Flowspace",
  },
  twitter: {
    card: "summary_large_image",
    title: "Flowspace - Modern Task Management",
    description: "Streamline your productivity with Flowspace",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#FAFAF9" },
    { media: "(prefers-color-scheme: dark)", color: "#0C0A09" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${sora.variable} ${dmSans.variable}`}
      suppressHydrationWarning
    >
      <body className="font-sans antialiased min-h-screen">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
