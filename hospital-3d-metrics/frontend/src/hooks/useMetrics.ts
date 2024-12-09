import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

interface Metric {
  floor: string;
  room?: string;
  metric_name: string;
  value: number;
  timestamp: string;
  metric_type: string;
}

interface DetailedMetrics {
  floorMetrics: Metric[];
  roomMetrics: Metric[];
  patientMetrics?: Metric[];
  staffMetrics?: Metric[];
}

export const useMetrics = () => {
  const [metrics, setMetrics] = useState<DetailedMetrics>({
    floorMetrics: [],
    roomMetrics: []
  });
  const [currentMetrics, setCurrentMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = 'http://localhost:8000/api/v1';

  const handleApiError = (err: any) => {
    console.error('API Error:', err);
    if (axios.isAxiosError(err)) {
      if (err.response?.status === 404) {
        return `No data found: ${err.response.data.detail || 'Resource not found'}`;
      }
      return err.response?.data?.detail || err.message;
    }
    return 'An unexpected error occurred';
  };

  // Fetch all initial metrics for overview mode
  const fetchAllMetrics = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/metrics`);
      if (response.data && Array.isArray(response.data)) {
        const floorLevelMetrics = response.data.filter(m => m.metric_type === 'floor');
        setCurrentMetrics(floorLevelMetrics);
        setMetrics({
          floorMetrics: floorLevelMetrics,
          roomMetrics: []
        });
      }
    } catch (err) {
      console.error('Error fetching all metrics:', err);
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchFloorMetrics = useCallback(async (floor: string) => {
    try {
      setLoading(true);
      const encodedFloor = encodeURIComponent(floor);
      const response = await axios.get(`${API_BASE_URL}/floors/${encodedFloor}/metrics`);

      if (response.data && Array.isArray(response.data)) {
        const floorLevelMetrics = response.data.filter(m => m.metric_type === 'floor');
        const roomLevelMetrics = response.data.filter(m => m.metric_type === 'room');

        setMetrics(prevMetrics => ({
          ...prevMetrics,
          floorMetrics: [
            ...prevMetrics.floorMetrics.filter(m => m.floor !== floor),
            ...floorLevelMetrics
          ],
          roomMetrics: [
            ...prevMetrics.roomMetrics.filter(m => m.floor !== floor),
            ...roomLevelMetrics
          ]
        }));

        setCurrentMetrics(prevMetrics => [
          ...prevMetrics.filter(m => m.floor !== floor),
          ...floorLevelMetrics
        ]);
      }
    } catch (err) {
      console.error('Error fetching floor metrics:', err);
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchHeatmapData = useCallback(async (floor: string, metricName: string) => {
    try {
      setLoading(true);
      const encodedFloor = encodeURIComponent(floor);
      const response = await axios.get(
        `${API_BASE_URL}/heatmap/${encodedFloor}`,
        { params: { metric_name: metricName } }
      );

      if (response.data && Array.isArray(response.data)) {
        const newMetrics = response.data.filter(m => m.metric_type === 'floor');

        setCurrentMetrics(prevMetrics => {
          const withoutFloor = prevMetrics.filter(m => m.floor !== floor);
          return [...withoutFloor, ...newMetrics];
        });

        // Also update the metrics state
        setMetrics(prevMetrics => ({
          ...prevMetrics,
          floorMetrics: [
            ...prevMetrics.floorMetrics.filter(m => m.floor !== floor),
            ...newMetrics
          ]
        }));
      }
    } catch (err) {
      console.error('Error fetching heatmap data:', err);
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data load
  useEffect(() => {
    fetchAllMetrics();
  }, [fetchAllMetrics]);

  useEffect(() => {
    console.log('Current metrics state:', currentMetrics);
  }, [currentMetrics]);

  return {
    metrics,
    loading,
    error,
    fetchFloorMetrics,
    fetchHeatmapData,
    currentMetrics,
    fetchAllMetrics
  };
};