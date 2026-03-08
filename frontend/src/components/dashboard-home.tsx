"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const quickActions = [
  {
    title: "Notebooks",
    description: "Manage your notebook library",
    href: "/notebooks",
    icon: (
      <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 19.5v-15A2.5 2.5 0 016.5 2H20v20H6.5a2.5 2.5 0 010-5H20" />
      </svg>
    ),
  },
  {
    title: "Chat",
    description: "Ask questions to your notebooks",
    href: "/chat",
    icon: (
      <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" />
      </svg>
    ),
  },
  {
    title: "Studio",
    description: "Generate audio, video, slides, and more",
    href: "/studio",
    icon: (
      <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="23,7 16,12 23,17" />
        <rect x="1" y="5" width="15" height="14" rx="2" />
      </svg>
    ),
  },
  {
    title: "Sources",
    description: "Upload files, URLs, and YouTube links",
    href: "/sources",
    icon: (
      <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
        <polyline points="14,2 14,8 20,8" />
      </svg>
    ),
  },
  {
    title: "Deep Research",
    description: "Run extended research on any topic",
    href: "/research",
    icon: (
      <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
    ),
  },
  {
    title: "Workflows",
    description: "Chain operations for automation",
    href: "/workflows",
    icon: (
      <svg className="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="16,3 21,3 21,8" />
        <line x1="4" y1="20" x2="21" y2="3" />
        <polyline points="21,16 21,21 16,21" />
        <line x1="15" y1="15" x2="21" y2="21" />
        <line x1="4" y1="4" x2="9" y2="9" />
      </svg>
    ),
  },
];

export function DashboardHome() {
  return (
    <div className="space-y-8">
      {/* Welcome */}
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">
          Your NotebookLM control center.
        </p>
      </div>

      {/* Quick Actions Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {quickActions.map((action) => (
          <Link key={action.href} href={action.href} className="group cursor-pointer">
            <Card className="h-full transition-all duration-200 hover:shadow-md hover:border-primary/20">
              <CardHeader className="flex flex-row items-center gap-4 pb-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-secondary text-foreground">
                  {action.icon}
                </div>
                <CardTitle className="text-base font-medium">
                  {action.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {action.description}
                </p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
