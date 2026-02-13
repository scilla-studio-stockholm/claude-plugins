import type { Metadata } from "next";
import { [FONT_IMPORT] } from "next/font/google";
import "./globals.css";

const fontFamily = [FONT_CONSTRUCTOR]({
  subsets: ["latin"],
  variable: "--font-[FONT_VAR]",
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  title: "[CLIENT_NAME] Prototype Kit",
  description: "Design system prototyping environment",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${fontFamily.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}
