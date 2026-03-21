import { create } from 'zustand';

export interface GraphNode {
  id: string;
  name: string;
  cvi: number;
  pagerank: number;
  blast_radius: number;
  budget_usd: number;
  is_commercially_backed: boolean;
}

export interface GraphLink {
  source: string;
  target: string;
}

export interface GraphState {
  nodes: GraphNode[];
  links: GraphLink[];
  isLoading: boolean;
  setGraphData: (data: { nodes: GraphNode[], links: GraphLink[] }) => void;
  resetGraph: () => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  nodes: [],
  links: [],
  isLoading: true,
  setGraphData: (data) => set(() => {
    // Diff-and-Merge limits reducing arbitrary DOM memory instantiation overhead
    // For direct binary parsing, complete object replacement ensures absolute consistency initially
    return { nodes: data.nodes, links: data.links, isLoading: false };
  }),
  resetGraph: () => set({ nodes: [], links: [], isLoading: true }),
}));
