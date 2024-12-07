// frontend/src/hooks/useMetrics.ts
import { useState, useEffect } from 'react';
import axios from 'axios';

interface Metric {
  floor: string;
  metric_name: string;
  value: number;
  timestamp: string;
}

interface UseMetricsReturn {
  metrics: Metric[];
  loading: boolean;
  error: string | null;
  fetchMetrics: (floor?: string, metricName?: string) => Promise<void>;
}

export const useMetrics = (): UseMetricsReturn => {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async (floor?: string, metricName?: string) => {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams();
      if (floor) params.append('floor', floor);
      if (metricName) params.append('metric_name', metricName);

      const response = await axios.get(`http://localhost:8000/api/metrics`, {
        params,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      console.log('API Response:', response.data); // Debug log
      setMetrics(response.data);
    } catch (err) {
      console.error('Error fetching metrics:', err); // Debug log
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return { metrics, loading, error, fetchMetrics };
};