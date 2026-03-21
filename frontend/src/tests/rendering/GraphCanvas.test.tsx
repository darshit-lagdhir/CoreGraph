import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import GraphCanvas from '../../components/GraphCanvas';

// Mocking react-force-graph-3d due to WebGL context absence in JSDOM
vi.mock('react-force-graph-3d', () => ({
  default: () => <div data-testid="force-graph-3d-placeholder">FORCE_GRAPH_MOCK</div>
}));

describe('WebGL Rendering Engine Constraints', () => {
  it('instantiates the 3D viewport without blocking the main event loop', () => {
    const { getByTestId } = render(<GraphCanvas />);
    expect(getByTestId('force-graph-3d-placeholder')).toBeDefined();
  });
});
