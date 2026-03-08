"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiGet, apiPost, apiDelete } from "@/lib/api-client";

export function useNotebooks() {
  return useQuery({
    queryKey: ["notebooks"],
    queryFn: () => apiGet<{ notebooks: string }>("/api/v1/notebooks"),
  });
}

export function useNotebookStats() {
  return useQuery({
    queryKey: ["notebook-stats"],
    queryFn: () => apiGet<{ stats: string }>("/api/v1/notebooks/stats"),
  });
}

export function useAddNotebook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      url: string;
      name: string;
      description?: string;
      topics?: string;
    }) => apiPost("/api/v1/notebooks", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notebooks"] });
      queryClient.invalidateQueries({ queryKey: ["notebook-stats"] });
    },
  });
}

export function useRemoveNotebook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiDelete(`/api/v1/notebooks/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notebooks"] });
      queryClient.invalidateQueries({ queryKey: ["notebook-stats"] });
    },
  });
}

export function useActivateNotebook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      apiPost(`/api/v1/notebooks/${id}/activate`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notebooks"] });
    },
  });
}

export function useSearchNotebooks(query: string) {
  return useQuery({
    queryKey: ["notebooks-search", query],
    queryFn: () =>
      apiGet<{ results: string }>(
        `/api/v1/notebooks/search?q=${encodeURIComponent(query)}`
      ),
    enabled: query.length > 0,
  });
}
