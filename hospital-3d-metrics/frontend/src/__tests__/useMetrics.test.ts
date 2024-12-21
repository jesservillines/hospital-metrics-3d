import { renderHook, act } from '@testing-library/react-hooks';
import { useMetrics } from '../hooks/useMetrics';
import { apiService } from '../services/api';
import { vi } from 'vitest';

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    getAllMetrics: vi.fn(),
    getFloorMetrics: vi.fn(),
    getRoomMetrics: vi.fn(),
  },
}));

describe('useMetrics', () => {
  const mockFloorMetrics = [
    {
      floor: '1 East',
      floor_id: '1E',
      metric_name: 'staff_satisfaction',
      value: 85.5,
      timestamp: '2024-01-01T00:00:00Z',
      metric_category: 'staff',
    },
  ];

  const mockRoomMetrics = [
    {
      room_id: '101A',
      floor: '1 East',
      floor_id: '1E',
      metric_name: 'occupancy',
      value: 1,
      timestamp: '2024-01-01T00:00:00Z',
      metric_category: 'room',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    (apiService.getAllMetrics as any).mockResolvedValue({
      floorMetrics: mockFloorMetrics,
      roomMetrics: mockRoomMetrics,
    });
  });

  it('should fetch metrics on mount', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useMetrics());

    // Initial state
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();

    await waitForNextUpdate();

    // After loading
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.metrics.floorMetrics).toEqual(mockFloorMetrics);
    expect(result.current.metrics.roomMetrics).toEqual(mockRoomMetrics);
  });

  it('should handle API errors', async () => {
    const error = new Error('API Error');
    (apiService.getAllMetrics as any).mockRejectedValue(error);

    const { result, waitForNextUpdate } = renderHook(() => useMetrics());

    await waitForNextUpdate();

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(error.message);
  });

  it('should fetch floor metrics', async () => {
    const floorMetrics = [...mockFloorMetrics];
    const roomMetrics = [...mockRoomMetrics];
    (apiService.getFloorMetrics as any).mockResolvedValue(floorMetrics);
    (apiService.getRoomMetrics as any).mockResolvedValue(roomMetrics);

    const { result } = renderHook(() => useMetrics());
    await act(async () => {
      await result.current.fetchFloorMetrics('1 East');
    });

    expect(apiService.getFloorMetrics).toHaveBeenCalledWith('1 East');
    expect(apiService.getRoomMetrics).toHaveBeenCalledWith('1 East');
    expect(result.current.metrics.floorMetrics).toEqual(floorMetrics);
    expect(result.current.metrics.roomMetrics).toEqual(roomMetrics);
  });

  it('should filter room metrics', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useMetrics());
    await waitForNextUpdate();

    const roomMetrics = result.current.getRoomMetrics('101A');
    expect(roomMetrics).toHaveLength(1);
    expect(roomMetrics[0].room_id).toBe('101A');
  });

  it('should filter floor metrics', async () => {
    const { result, waitForNextUpdate } = renderHook(() => useMetrics());
    await waitForNextUpdate();

    const floorMetrics = result.current.getFloorMetrics('1 East');
    expect(floorMetrics).toHaveLength(1);
    expect(floorMetrics[0].floor).toBe('1 East');
  });
});
