import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mocking the browser-specific ResizeObserver bounding limits
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

vi.stubGlobal('ResizeObserver', ResizeObserver);
