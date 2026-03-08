"use client";

import { useAuth } from "@/contexts/auth-context";
import { LoginPage } from "@/components/layout/login-page";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { DashboardHome } from "@/components/dashboard-home";

export default function Home() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <DashboardShell>
      <DashboardHome />
    </DashboardShell>
  );
}
