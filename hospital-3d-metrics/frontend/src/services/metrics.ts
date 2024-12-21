import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface Metric {
  floor_id: string;
  metric_name: string;
  value: number;
  metric_category: string;
  timestamp: string;
}

export interface RoomMetric extends Metric {
  room_id: string;
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true,
});

// Add request interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized error (e.g., redirect to login)
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const fetchFloorMetrics = async (floorId: string, token: string): Promise<Metric[]> => {
  try {
    const response = await api.get(`/metrics/floors/${floorId}`, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching floor metrics:', error);
    throw new Error('Failed to fetch floor metrics');
  }
};

export const fetchRoomMetrics = async (floorId: string, token: string): Promise<RoomMetric[]> => {
  try {
    const response = await api.get(`/metrics/floors/${floorId}/rooms`, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching room metrics:', error);
    throw new Error('Failed to fetch room metrics');
  }
};

export const fetchFloorRoomMetrics = async (floorId: string, token: string): Promise<RoomMetric[]> => {
  try {
    const response = await api.get(`/metrics/floors/${floorId}/rooms/all`, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching floor room metrics:', error);
    throw new Error('Failed to fetch floor room metrics');
  }
};

export const fetchSpecificRoomMetrics = async (
  floorId: string,
  roomId: string,
  token: string
): Promise<RoomMetric[]> => {
  try {
    const response = await api.get(`/metrics/floors/${floorId}/rooms/${roomId}`, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching specific room metrics:', error);
    throw new Error('Failed to fetch specific room metrics');
  }
};
