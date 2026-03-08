"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/auth-context";
import { LoginPage } from "@/components/layout/login-page";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { apiPost, apiGet } from "@/lib/api-client";
import { toast } from "sonner";

const generationTypes = [
  { key: "audio", label: "Audio", endpoint: "/api/v1/studio/audio", icon: "M9 18V5l12-2v13" },
  { key: "video", label: "Video", endpoint: "/api/v1/studio/video", icon: "M23,7 16,12 23,17" },
  { key: "slides", label: "Slides", endpoint: "/api/v1/studio/slides", icon: "M2 3h20v14H2z M8 21h8 M12 17v4" },
  { key: "mindmap", label: "Mind Map", endpoint: "/api/v1/studio/mindmap", icon: "M12 2a4 4 0 014 4c0 1.1-.9 2-2 2" },
  { key: "infographic", label: "Infographic", endpoint: "/api/v1/studio/infographic", icon: "M18 20V10 M12 20V4 M6 20v-6" },
  { key: "datatable", label: "Data Table", endpoint: "/api/v1/studio/datatable", icon: "M3 3h18v18H3z M3 9h18 M3 15h18 M9 3v18" },
];

const reportTypes = [
  { key: "study_guide", label: "Study Guide" },
  { key: "faq", label: "FAQ" },
  { key: "timeline", label: "Timeline" },
  { key: "briefing_doc", label: "Briefing Doc" },
];

function StudioPage() {
  const [notebookUrl, setNotebookUrl] = useState("");
  const [customPrompt, setCustomPrompt] = useState("");
  const [audioFormat, setAudioFormat] = useState("deep_dive");
  const [reportType, setReportType] = useState("study_guide");
  const [generating, setGenerating] = useState(false);
  const [activeGen, setActiveGen] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);

  const handleGenerate = async (type: string, endpoint: string) => {
    if (!notebookUrl) {
      toast.error("Please enter a notebook URL");
      return;
    }

    setGenerating(true);
    setActiveGen(type);
    setResult(null);

    try {
      const body: Record<string, string> = { notebook_url: notebookUrl };
      if (customPrompt) body.custom_prompt = customPrompt;
      if (type === "audio") body.format = audioFormat;

      const task = await apiPost<{ task_id: string }>(endpoint, body);

      // Poll
      let res = await apiGet<{ status: string; result?: string; error?: string }>(
        `/api/v1/chat/tasks/${task.task_id}`
      );

      while (res.status === "queued" || res.status === "running") {
        await new Promise((r) => setTimeout(r, 3000));
        res = await apiGet(`/api/v1/chat/tasks/${task.task_id}`);
      }

      if (res.status === "completed") {
        setResult(res.result || "Generation completed successfully");
        toast.success(`${type} generated successfully`);
      } else {
        toast.error(res.error || "Generation failed");
      }
    } catch {
      toast.error("Generation failed");
    } finally {
      setGenerating(false);
      setActiveGen(null);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Studio</h1>
        <p className="mt-1 text-muted-foreground">
          Generate content from your notebooks
        </p>
      </div>

      {/* Notebook URL Input */}
      <Card>
        <CardContent className="space-y-4 pt-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Notebook URL</label>
            <Input
              placeholder="https://notebooklm.google.com/notebook/..."
              value={notebookUrl}
              onChange={(e) => setNotebookUrl(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Custom Prompt (optional)</label>
            <Textarea
              placeholder="Focus on chapter 3 and key findings..."
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              rows={2}
            />
          </div>
        </CardContent>
      </Card>

      {/* Generation Types Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {generationTypes.map((gen) => (
          <Card
            key={gen.key}
            className={`transition-all duration-200 ${
              activeGen === gen.key ? "ring-2 ring-primary" : "hover:shadow-md hover:border-primary/20"
            }`}
          >
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-3 text-base font-medium">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary">
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d={gen.icon} />
                  </svg>
                </div>
                {gen.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {gen.key === "audio" && (
                <div className="mb-3">
                  <Select value={audioFormat} onValueChange={setAudioFormat}>
                    <SelectTrigger className="cursor-pointer">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="deep_dive">Deep Dive</SelectItem>
                      <SelectItem value="brief">Brief</SelectItem>
                      <SelectItem value="critique">Critique</SelectItem>
                      <SelectItem value="debate">Debate</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
              <Button
                className="w-full cursor-pointer"
                disabled={generating || !notebookUrl}
                onClick={() => handleGenerate(gen.key, gen.endpoint)}
              >
                {activeGen === gen.key ? "Generating..." : "Generate"}
              </Button>
            </CardContent>
          </Card>
        ))}

        {/* Reports Card */}
        <Card className="transition-all duration-200 hover:shadow-md hover:border-primary/20">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-base font-medium">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-secondary">
                <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                  <polyline points="14,2 14,8 20,8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
              </div>
              Reports
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Select value={reportType} onValueChange={setReportType}>
              <SelectTrigger className="cursor-pointer">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {reportTypes.map((rt) => (
                  <SelectItem key={rt.key} value={rt.key}>
                    {rt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              className="w-full cursor-pointer"
              disabled={generating || !notebookUrl}
              onClick={() =>
                handleGenerate("report", `/api/v1/studio/reports/${reportType}`)
              }
            >
              {activeGen === "report" ? "Generating..." : "Generate Report"}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Result */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Result</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-96 overflow-auto whitespace-pre-wrap text-sm text-muted-foreground">
              {result}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function Studio() {
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
      <StudioPage />
    </DashboardShell>
  );
}
