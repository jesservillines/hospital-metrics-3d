import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { 
  fetchFloorMetrics as fetchFloorMetricsApi,
  fetchRoomMetrics as fetchRoomMetricsApi,
  fetchFloorRoomMetrics as fetchFloorRoomMetricsApi,
  fetchSpecificRoomMetrics as fetchSpecificRoomMetricsApi,
  type Metric as ApiMetric
} from '@/services/metrics';

interface Metric {
  floor_id: string;
  metric_name: string;
  value: number;
  timestamp: string;
  metric_category: string;
  metric_type: 'floor' | 'room';
  room_id?: string;
}

interface DetailedMetrics {
  floorMetrics: Metric[];
  roomMetrics: Metric[];
}

const transformApiMetric = (apiMetric: ApiMetric): Metric => ({
  ...apiMetric,
  metric_type: 'floor'
});

export const useMetrics = () => {
  const { accessToken } = useAuth();
  const [metrics, setMetrics] = useState<DetailedMetrics>({
    floorMetrics: [],
    roomMetrics: []
  });
  const [currentMetrics, setCurrentMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleApiError = (err: any) => {
    console.error('API Error:', err);
    if (err.response) {
      console.error('Response data:', err.response.data);
      return err.response.data.detail || err.message;
    }
    return err.message || 'An unexpected error occurred';
  };

  const fetchAllFloorMetrics = useCallback(async () => {
    if (!accessToken) {
      console.error('No access token available');
      setError('Authentication required');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Fetch metrics for all floors
      const westFloors = ['1_west', '2_west', '3_west', '4_west'];
      const eastFloors = ['1_east', '2_east', '3_east'];
      const allFloors = [...westFloors, ...eastFloors];
      
      const allMetrics = await Promise.all(
        allFloors.map(floor => fetchFloorMetricsApi(floor, accessToken))
      );
      
      const flattenedMetrics = allMetrics.flat().map(transformApiMetric);
      setCurrentMetrics(flattenedMetrics);
      
    } catch (err) {
      setError(handleApiError(err));
      console.error('Error fetching all floor metrics:', err);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  const fetchMetricsForFloor = useCallback(async (floor: string) => {
    if (!accessToken) {
      console.error('No access token available');
      setError('Authentication required');
      return [];
    }
    
    try {
      setLoading(true);
      const floorMetrics = await fetchFloorMetricsApi(floor, accessToken);
      const roomMetrics = await fetchRoomMetricsApi(floor, accessToken);
      
      setMetrics({
        floorMetrics: floorMetrics.map(transformApiMetric),
        roomMetrics: roomMetrics.map(m => ({ ...transformApiMetric(m), metric_type: 'room' }))
      });
      
      return floorMetrics;
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      return [];
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  const fetchFloorRoomMetrics = useCallback(async (floor: string) => {
    if (!accessToken) {
      console.error('No access token available');
      setError('Authentication required');
      return;
    }
    
    try {
      setLoading(true);
      const data = await fetchFloorRoomMetricsApi(floor, accessToken);
      setCurrentMetrics(data.map(transformApiMetric));
    } catch (err) {
      setError(handleApiError(err));
      console.error('Error fetching floor room metrics:', err);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  const fetchSpecificRoomMetrics = useCallback(async (floor: string, room: string) => {
    if (!accessToken) {
      console.error('No access token available');
      setError('Authentication required');
      return;
    }
    
    try {
      setLoading(true);
      const data = await fetchSpecificRoomMetricsApi(floor, room, accessToken);
      setCurrentMetrics(data.map(transformApiMetric));
    } catch (err) {
      setError(handleApiError(err));
      console.error('Error fetching specific room metrics:', err);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  return {
    metrics,
    currentMetrics,
    loading,
    error,
    fetchMetricsForFloor,
    fetchFloorRoomMetrics,
    fetchSpecificRoomMetrics,
    fetchAllFloorMetrics,
  };
};