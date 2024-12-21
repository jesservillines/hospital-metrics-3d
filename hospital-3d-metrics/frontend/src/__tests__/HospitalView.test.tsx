import { render, screen, waitFor } from '@testing-library/react';
import { HospitalView } from '../components/HospitalView';
import { useMetrics } from '../hooks/useMetrics';
import { vi } from 'vitest';

// Mock the useMetrics hook
vi.mock('../hooks/useMetrics');

// Mock Three.js components
vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('@react-three/drei', () => ({
  OrbitControls: () => null,
  PerspectiveCamera: () => null,
}));

describe('HospitalView', () => {
  const mockMetrics = {
    floorMetrics: [
      {
        floor: '1 East',
        floor_id: '1E',
        metric_name: 'staff_satisfaction',
        value: 85.5,
        timestamp: '2024-01-01T00:00:00Z',
        metric_category: 'staff',
      },
    ],
    roomMetrics: [
      {
        room_id: '101A',
        floor: '1 East',
        floor_id: '1E',
        metric_name: 'occupancy',
        value: 1,
        timestamp: '2024-01-01T00:00:00Z',
        metric_category: 'room',
      },
    ],
  };

  beforeEach(() => {
    (useMetrics as any).mockReturnValue({
      metrics: mockMetrics,
      loading: false,
      error: null,
      fetchFloorMetrics: vi.fn(),
      getRoomMetrics: vi.fn(),
      getFloorMetrics: vi.fn(),
    });
  });

  it('should render loading state', () => {
    (useMetrics as any).mockReturnValue({
      metrics: { floorMetrics: [], roomMetrics: [] },
      loading: true,
      error: null,
    });

    render(<HospitalView />);
    expect(screen.getByText(/loading hospital data/i)).toBeInTheDocument();
  });

  it('should render error state', () => {
    (useMetrics as any).mockReturnValue({
      metrics: { floorMetrics: [], roomMetrics: [] },
      loading: false,
      error: 'Failed to load data',
    });

    render(<HospitalView />);
    expect(screen.getByText(/error loading hospital data/i)).toBeInTheDocument();
    expect(screen.getByText(/failed to load data/i)).toBeInTheDocument();
  });

  it('should render hospital view with metrics', async () => {
    render(<HospitalView />);

    await waitFor(() => {
      expect(screen.queryByText(/loading hospital data/i)).not.toBeInTheDocument();
    });

    // Check for building components
    expect(screen.getByTestId('building-east')).toBeInTheDocument();
    expect(screen.getByTestId('building-west')).toBeInTheDocument();
  });

  it('should fetch floor metrics when floor is selected', async () => {
    const mockFetchFloorMetrics = vi.fn();
    (useMetrics as any).mockReturnValue({
      metrics: mockMetrics,
      loading: false,
      error: null,
      fetchFloorMetrics: mockFetchFloorMetrics,
    });

    render(<HospitalView />);

    // Simulate floor selection
    const floorButton = screen.getByTestId('floor-1-east');
    floorButton.click();

    await waitFor(() => {
      expect(mockFetchFloorMetrics).toHaveBeenCalledWith('1 East');
    });
  });

  it('should update metrics panel when room is selected', async () => {
    render(<HospitalView />);

    // Simulate room selection
    const roomElement = screen.getByTestId('room-101a');
    roomElement.click();

    await waitFor(() => {
      const metricsPanel = screen.getByTestId('metrics-panel');
      expect(metricsPanel).toHaveTextContent('Room 101A');
      expect(metricsPanel).toHaveTextContent('Occupancy: 1');
    });
  });
});
