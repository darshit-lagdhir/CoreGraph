import { create } from 'zustand';

export interface GraphNode {
  id: string;
  name: string;
  cvi: number;
  pagerank: number;
  blast_radius: number;
  budget_usd: number;
  is_commercially_backed: boolean;
  cluster_id?: number;
  community_risk?: number;
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
  selectedNode: GraphNode | null;
  setSelectedNode: (node: GraphNode | null) => void;
  selectedPath: string[]; // List of node IDs
  setSelectedPath: (path: string[]) => void;
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
  resetGraph: () => set({ nodes: [], links: [], isLoading: true, selectedNode: null, selectedPath: [] }),
  selectedNode: null,
  setSelectedNode: (node) => set({ selectedNode: node }),
  selectedPath: [],
  setSelectedPath: (path) => set({ selectedPath: path }),
}));
