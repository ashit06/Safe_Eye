import "./globals.css"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Safe Eye",
  description: "Smart Road Safety System",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
