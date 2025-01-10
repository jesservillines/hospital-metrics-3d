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
    console.log(`Fetching metrics for floor: ${floorId}`);
    const response = await api.get(`/metrics/floors/${floorId}`, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    console.log(`Received metrics for floor ${floorId}:`, response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching floor metrics:', error);
    throw new Error('Failed to fetch floor metrics');
  }
};

export const fetchRoomMetrics = async (floorId: string, token: string): Promise<RoomMetric[]> => {
  try {
    console.log(`Fetching room metrics for floor: ${floorId}`);
    const response = await api.get(`/metrics/floors/${floorId}/rooms`, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    console.log(`Received room metrics for floor ${floorId}:`, response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching room metrics:', error);
    throw new Error('Failed to fetch room metrics');
  }
};

export const fetchFloorRoomMetrics = async (floorId: string, token: string): Promise<RoomMetric[]> => {
  try {
    console.log(`Fetching all room metrics for floor: ${floorId}`);
    const response = await api.get(`/metrics/floors/${floorId}/rooms`, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    
    if (!response.data) {
      console.warn(`No room metrics data received for floor ${floorId}`);
      return [];
    }
    
    if (!Array.isArray(response.data)) {
      console.error(`Invalid response data format for floor ${floorId}:`, response.data);
      throw new Error('Invalid response data format');
    }
    
    console.log(`Received all room metrics for floor ${floorId}:`, response.data);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching floor room metrics:', {
      error,
      status: error.response?.status,
      data: error.response?.data,
      floorId
    });
    
    if (error.response?.status === 404) {
      console.log(`No room metrics found for floor ${floorId}`);
      return [];
    }
    
    if (error.response?.status === 401) {
      throw new Error('Authentication required');
    }
    
    if (error.response?.status === 403) {
      throw new Error('Not authorized to access these metrics');
    }
    
    throw new Error(error.response?.data?.detail || 'Failed to fetch floor room metrics');
  }
};

export const fetchSpecificRoomMetrics = async (
  floorId: string,
  roomId: string,
  token: string
): Promise<RoomMetric[]> => {
  try {
    console.log(`Fetching metrics for room ${roomId} on floor: ${floorId}`);
    const response = await api.get(`/metrics/floors/${floorId}/rooms/${roomId}`, {
      headers: { 
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    });
    
    if (!response.data) {
      console.warn(`No metrics data received for room ${roomId} on floor ${floorId}`);
      return [];
    }
    
    console.log(`Received metrics for room ${roomId} on floor ${floorId}:`, response.data);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching specific room metrics:', {
      error,
      status: error.response?.status,
      data: error.response?.data,
      floorId,
      roomId
    });
    
    if (error.response?.status === 404) {
      console.log(`No metrics found for room ${roomId} on floor ${floorId}`);
      return [];
    }
    
    throw new Error('Failed to fetch specific room metrics');
  }
};
