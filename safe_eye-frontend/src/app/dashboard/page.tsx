"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import Dashboard from "@/components/dashboard"
import { isAuthenticated } from "@/lib/auth"

export default function DashboardPage() {
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login")
    }
  }, [])

  return <Dashboard />
}
