"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/auth-context";
import { LoginPage } from "@/components/layout/login-page";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { apiPost, apiGet } from "@/lib/api-client";
import { toast } from "sonner";

interface Message {
  role: "user" | "assistant";
  content: string;
}

function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const task = await apiPost<{ task_id: string; status: string }>(
        "/api/v1/chat/ask",
        { question }
      );

      // Poll for result
      let result = await apiGet<{
        status: string;
        result?: string;
        error?: string;
      }>(`/api/v1/chat/tasks/${task.task_id}`);

      while (result.status === "queued" || result.status === "running") {
        await new Promise((r) => setTimeout(r, 2000));
        result = await apiGet(`/api/v1/chat/tasks/${task.task_id}`);
      }

      if (result.status === "completed" && result.result) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: result.result! },
        ]);
      } else {
        toast.error(result.error || "Failed to get answer");
      }
    } catch (e) {
      toast.error("Failed to send question");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-semibold tracking-tight">Chat</h1>
        <p className="mt-1 text-muted-foreground">
          Ask questions to your notebooks
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 space-y-4 overflow-y-auto pb-4">
        {messages.length === 0 && (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-muted-foreground/30"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" />
              </svg>
              <p className="mt-4 text-sm text-muted-foreground">
                Ask a question to get started
              </p>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <Card
              className={`max-w-[80%] ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary"
              }`}
            >
              <CardContent className="px-4 py-3">
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </CardContent>
            </Card>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <Card className="bg-secondary">
              <CardContent className="px-4 py-3">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                  Thinking...
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-3 border-t pt-4">
        <Textarea
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          className="min-h-[44px] resize-none"
          disabled={loading}
        />
        <Button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className="shrink-0 cursor-pointer"
          size="icon"
        >
          <svg
            className="h-4 w-4"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22,2 15,22 11,13 2,9" />
          </svg>
        </Button>
      </div>
    </div>
  );
}

export default function Chat() {
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
      <ChatPage />
    </DashboardShell>
  );
}
