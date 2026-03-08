"use client";

import { useState } from "react";
import { useNotebooks, useAddNotebook, useRemoveNotebook, useActivateNotebook } from "@/hooks/use-notebooks";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { toast } from "sonner";

export function NotebooksPage() {
  const { data, isLoading } = useNotebooks();
  const addNotebook = useAddNotebook();
  const removeNotebook = useRemoveNotebook();
  const activateNotebook = useActivateNotebook();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState({
    url: "",
    name: "",
    description: "",
    topics: "",
  });

  const handleAdd = async () => {
    if (!form.url || !form.name) {
      toast.error("URL and name are required");
      return;
    }
    try {
      await addNotebook.mutateAsync(form);
      toast.success("Notebook added");
      setDialogOpen(false);
      setForm({ url: "", name: "", description: "", topics: "" });
    } catch (e) {
      toast.error("Failed to add notebook");
    }
  };

  const handleRemove = async (id: string) => {
    try {
      await removeNotebook.mutateAsync(id);
      toast.success("Notebook removed");
    } catch {
      toast.error("Failed to remove notebook");
    }
  };

  const handleActivate = async (id: string) => {
    try {
      await activateNotebook.mutateAsync(id);
      toast.success("Notebook activated");
    } catch {
      toast.error("Failed to activate notebook");
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Notebooks</h1>
          <p className="mt-1 text-muted-foreground">
            Manage your NotebookLM library
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="cursor-pointer gap-2">
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              Add Notebook
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Add Notebook</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Notebook URL</label>
                <Input
                  placeholder="https://notebooklm.google.com/notebook/..."
                  value={form.url}
                  onChange={(e) => setForm({ ...form, url: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Name</label>
                <Input
                  placeholder="My Research Notebook"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Textarea
                  placeholder="Brief description of this notebook..."
                  value={form.description}
                  onChange={(e) =>
                    setForm({ ...form, description: e.target.value })
                  }
                  rows={3}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Topics</label>
                <Input
                  placeholder="AI, Research, Marketing"
                  value={form.topics}
                  onChange={(e) => setForm({ ...form, topics: e.target.value })}
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <Button
                  variant="ghost"
                  onClick={() => setDialogOpen(false)}
                  className="cursor-pointer"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleAdd}
                  disabled={addNotebook.isPending}
                  className="cursor-pointer"
                >
                  {addNotebook.isPending ? "Adding..." : "Add"}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Notebook List */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-5 w-32 rounded bg-muted" />
              </CardHeader>
              <CardContent>
                <div className="h-4 w-full rounded bg-muted" />
                <div className="mt-2 h-4 w-2/3 rounded bg-muted" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data?.notebooks ? (
            <Card className="border-dashed">
              <CardContent className="flex items-center justify-center py-12">
                <pre className="max-h-64 overflow-auto text-xs text-muted-foreground whitespace-pre-wrap">
                  {data.notebooks}
                </pre>
              </CardContent>
            </Card>
          ) : (
            <Card className="border-dashed sm:col-span-2 lg:col-span-3">
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <svg
                  className="h-12 w-12 text-muted-foreground/40"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M4 19.5v-15A2.5 2.5 0 016.5 2H20v20H6.5a2.5 2.5 0 010-5H20" />
                </svg>
                <p className="mt-4 text-sm font-medium text-muted-foreground">
                  No notebooks yet
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Add a notebook to get started
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
