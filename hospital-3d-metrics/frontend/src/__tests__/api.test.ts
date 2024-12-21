import { apiService } from '../services/api';
import axios from 'axios';
import { vi } from 'vitest';

// Mock axios
vi.mock('axios');

describe('apiService', () => {
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
  });

  describe('getFloorMetrics', () => {
    it('should fetch floor metrics without floor parameter', async () => {
      (axios.get as any).mockResolvedValue({ data: mockFloorMetrics });

      const result = await apiService.getFloorMetrics();
      expect(result).toEqual(mockFloorMetrics);
      expect(axios.get).toHaveBeenCalledWith('/floors/metrics');
    });

    it('should fetch floor metrics with floor parameter', async () => {
      (axios.get as any).mockResolvedValue({ data: mockFloorMetrics });

      const result = await apiService.getFloorMetrics('1 East');
      expect(result).toEqual(mockFloorMetrics);
      expect(axios.get).toHaveBeenCalledWith('/floors/1%20East/metrics');
    });

    it('should handle API errors', async () => {
      const error = new Error('API Error');
      (axios.get as any).mockRejectedValue(error);

      await expect(apiService.getFloorMetrics()).rejects.toThrow('API Error');
    });
  });

  describe('getRoomMetrics', () => {
    it('should fetch all room metrics', async () => {
      (axios.get as any).mockResolvedValue({ data: mockRoomMetrics });

      const result = await apiService.getRoomMetrics();
      expect(result).toEqual(mockRoomMetrics);
      expect(axios.get).toHaveBeenCalledWith('/rooms/metrics');
    });

    it('should fetch room metrics for a specific floor', async () => {
      (axios.get as any).mockResolvedValue({ data: mockRoomMetrics });

      const result = await apiService.getRoomMetrics('1 East');
      expect(result).toEqual(mockRoomMetrics);
      expect(axios.get).toHaveBeenCalledWith('/floors/1%20East/rooms/metrics');
    });

    it('should fetch metrics for a specific room', async () => {
      (axios.get as any).mockResolvedValue({ data: mockRoomMetrics });

      const result = await apiService.getRoomMetrics('1 East', '101A');
      expect(result).toEqual(mockRoomMetrics);
      expect(axios.get).toHaveBeenCalledWith('/floors/1%20East/rooms/101A/metrics');
    });

    it('should handle API errors', async () => {
      const error = new Error('API Error');
      (axios.get as any).mockRejectedValue(error);

      await expect(apiService.getRoomMetrics()).rejects.toThrow('API Error');
    });
  });

  describe('getAllMetrics', () => {
    it('should fetch all metrics', async () => {
      (axios.get as any)
        .mockResolvedValueOnce({ data: mockFloorMetrics })
        .mockResolvedValueOnce({ data: mockRoomMetrics });

      const result = await apiService.getAllMetrics();
      expect(result).toEqual({
        floorMetrics: mockFloorMetrics,
        roomMetrics: mockRoomMetrics,
      });
    });

    it('should handle API errors', async () => {
      const error = new Error('API Error');
      (axios.get as any).mockRejectedValue(error);

      await expect(apiService.getAllMetrics()).rejects.toThrow('API Error');
    });
  });
});
