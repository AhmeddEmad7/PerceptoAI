import type React from "react"
import { Sidebar } from "@/components/sidebar"

export default function ConversationsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-auto w-full">{children}</main>
    </div>
  )
}
