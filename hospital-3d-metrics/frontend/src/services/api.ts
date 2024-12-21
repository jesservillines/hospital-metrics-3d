import axios from 'axios';

// Load API URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface FloorMetric {
  floor: string;
  floor_id: string;
  metric_name: string;
  value: number;
  timestamp: string;
  metric_category: string;
  meta_data?: any;
}

export interface RoomMetric {
  room_id: string;
  floor: string;
  floor_id: string;
  metric_name: string;
  value: number;
  timestamp: string;
  metric_category: string;
  meta_data?: any;
}

export const apiService = {
  // Floor endpoints
  async getFloorMetrics(floor?: string) {
    try {
      const endpoint = floor ? `/floors/${encodeURIComponent(floor)}/metrics` : '/floors/metrics';
      const response = await api.get<FloorMetric[]>(endpoint);
      return response.data;
    } catch (error) {
      console.error('Error fetching floor metrics:', error);
      throw error;
    }
  },

  // Room endpoints
  async getRoomMetrics(floor?: string, roomId?: string) {
    try {
      let endpoint = '/rooms/metrics';
      if (floor && roomId) {
        endpoint = `/floors/${encodeURIComponent(floor)}/rooms/${encodeURIComponent(roomId)}/metrics`;
      } else if (floor) {
        endpoint = `/floors/${encodeURIComponent(floor)}/rooms/metrics`;
      }
      const response = await api.get<RoomMetric[]>(endpoint);
      return response.data;
    } catch (error) {
      console.error('Error fetching room metrics:', error);
      throw error;
    }
  },

  // Utility function to fetch all metrics for initial load
  async getAllMetrics() {
    try {
      const [floorMetrics, roomMetrics] = await Promise.all([
        this.getFloorMetrics(),
        this.getRoomMetrics()
      ]);
      return {
        floorMetrics,
        roomMetrics
      };
    } catch (error) {
      console.error('Error fetching all metrics:', error);
      throw error;
    }
  }
};

export default apiService;
