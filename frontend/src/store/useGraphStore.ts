import { create } from 'zustand';

export interface NodeData {
  id: string;
  name: string;
  ecosystem: string;
  pagerank: number;
  blast_radius: number;
  cvi: number;
  budget: number;
  maintainers: number;
  val?: number;
  color?: string;
}

export interface LinkData {
  source: string;
  target: string;
}

export interface GraphPayload {
  nodes: NodeData[];
  links: LinkData[];
}

interface GraphStore {
  graphData: GraphPayload;
  isLoading: boolean;
  selectedNode: NodeData | null;
  setGraphData: (data: GraphPayload) => void;
  setIsLoading: (loading: boolean) => void;
  setSelectedNode: (node: NodeData | null) => void;
}

export const useGraphStore = create<GraphStore>((set) => ({
  graphData: { nodes: [], links: [] },
  isLoading: true,
  selectedNode: null,
  setGraphData: (data) => set({ graphData: data }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  setSelectedNode: (node) => set({ selectedNode: node }),
}));
