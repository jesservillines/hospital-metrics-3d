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

  const fetchMetricsForFloor = useCallback(async (floor: string) => {
    try {
      const encodedFloor = encodeURIComponent(floor);
      // Fetch all metrics for the floor
      const response = await axios.get(`${API_BASE_URL}/floors/${encodedFloor}/metrics`);
      console.log(`Received metrics for floor ${floor}:`, response.data);

      if (response.data && Array.isArray(response.data)) {
        return response.data.filter(m => m.metric_type === 'floor');
      }
      return [];
    } catch (err) {
      console.error(`Error fetching metrics for floor ${floor}:`, err);
      return [];
    }
  }, []);

  const fetchAllFloorMetrics = useCallback(async () => {
    try {
      setLoading(true);
      const floors = [
        '1 East', '2 East', '3 East',
        '1 West', '2 West', '3 West', '4 West'
      ];

      const allMetricsPromises = floors.map(floor => fetchMetricsForFloor(floor));
      const allMetricsArrays = await Promise.all(allMetricsPromises);

      // Combine all floor metrics
      const combinedMetrics = allMetricsArrays.flat();
      console.log('Combined floor metrics:', combinedMetrics);

      setCurrentMetrics(combinedMetrics);
      setMetrics(prevMetrics => ({
        ...prevMetrics,
        floorMetrics: combinedMetrics
      }));
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  }, [fetchMetricsForFloor]);

  const fetchFloorMetrics = useCallback(async (floor: string) => {
    try {
      setLoading(true);
      const floorMetrics = await fetchMetricsForFloor(floor);

      setCurrentMetrics(prevMetrics => {
        const otherFloors = prevMetrics.filter(m => m.floor !== floor);
        return [...otherFloors, ...floorMetrics];
      });

      setMetrics(prevMetrics => ({
        ...prevMetrics,
        floorMetrics: [
          ...prevMetrics.floorMetrics.filter(m => m.floor !== floor),
          ...floorMetrics
        ]
      }));
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  }, [fetchMetricsForFloor]);

  const fetchHeatmapData = useCallback(async (floor: string, metricName: string) => {
    try {
      setLoading(true);
      const encodedFloor = encodeURIComponent(floor);
      const response = await axios.get(
        `${API_BASE_URL}/heatmap/${encodedFloor}`,
        { params: { metric_name: metricName } }
      );

      if (response.data && Array.isArray(response.data)) {
        // Keep existing metrics and only update the heatmap metric
        setCurrentMetrics(prevMetrics => {
          const existingMetrics = prevMetrics.filter(m =>
            m.floor !== floor || m.metric_name !== metricName
          );
          return [...existingMetrics, ...response.data];
        });
      }
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  // Initialize metrics on mount
  useEffect(() => {
    fetchAllFloorMetrics();
  }, [fetchAllFloorMetrics]);

  // Debug log current metrics state
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
    fetchAllFloorMetrics
  };
};