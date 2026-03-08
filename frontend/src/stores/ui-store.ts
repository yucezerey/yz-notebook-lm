import { create } from "zustand";

interface UIStore {
  sidebarOpen: boolean;
  activeNotebookId: string | null;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setActiveNotebook: (id: string | null) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  activeNotebookId: null,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setActiveNotebook: (id) => set({ activeNotebookId: id }),
}));
