"use client";

import { useAuth } from "@/contexts/auth-context";
import { LoginPage } from "@/components/layout/login-page";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { NotebooksPage } from "@/components/notebooks/notebooks-page";

export default function Notebooks() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!user) return <LoginPage />;

  return (
    <DashboardShell>
      <NotebooksPage />
    </DashboardShell>
  );
}
