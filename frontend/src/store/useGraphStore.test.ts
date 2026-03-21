import { describe, it, expect, beforeEach } from 'vitest';
import { useGraphStore } from './useGraphStore';

describe('Graph Memory Architecture Limits', () => {
  beforeEach(() => {
    useGraphStore.getState().resetGraph();
  });

  it('verifies explicit node matrix instantiation logic', () => {
    const mockData = {
      nodes: [
        { id: '123', name: 'react', cvi: 10, pagerank: 0.8, blast_radius: 500, budget_usd: 1000, is_commercially_backed: true }
      ],
      links: []
    };

    useGraphStore.getState().setGraphData(mockData);

    const memoryState = useGraphStore.getState();
    expect(memoryState.nodes.length).toBe(1);
    expect(memoryState.nodes[0].name).toBe('react');
    expect(memoryState.isLoading).toBe(false);
  });

  it('validates volatile memory wiping structures', () => {
    const mockData = {
      nodes: [
        { id: '456', name: 'vue', cvi: 12, pagerank: 0.5, blast_radius: 100, budget_usd: 0, is_commercially_backed: false }
      ],
      links: []
    };

    useGraphStore.getState().setGraphData(mockData);
    expect(useGraphStore.getState().nodes.length).toBe(1);

    useGraphStore.getState().resetGraph();
    expect(useGraphStore.getState().nodes.length).toBe(0);
    expect(useGraphStore.getState().isLoading).toBe(true);
  });
});
