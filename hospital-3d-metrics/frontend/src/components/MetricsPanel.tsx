// MetricsPanel.tsx
import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface Metric {
  floor_id: string;
  metric_name: string;
  value: number;
  timestamp: string;
  metric_category: string;
  metric_type: 'floor' | 'room';
  room_id?: string;
}

interface MetricsPanelProps {
  hoveredFloor: string | null;
  selectedFloor: string | null;
  metrics: Metric[];
  selectedCategories: string[];
  selectedMetrics: string[];
  showFloorDetail?: boolean;
  onClose?: () => void;
}

interface MetricGroups {
  'Patient Metrics': Metric[];
  'Staff Metrics': Metric[];
  [key: string]: Metric[];
}

export function MetricsPanel({
  hoveredFloor,
  selectedFloor,
  metrics,
  selectedCategories,
  selectedMetrics,
  showFloorDetail = false,
  onClose
}: MetricsPanelProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const displayFloor = selectedFloor || hoveredFloor;

  useEffect(() => {
    if (hoveredFloor || selectedFloor) {
      setIsVisible(true);
    } else {
      const timer = setTimeout(() => setIsVisible(false), 300);
      return () => clearTimeout(timer);
    }
  }, [hoveredFloor, selectedFloor]);

  useEffect(() => {
    try {
      // Reset error state when props change
      setError(null);
      
      // Validate metrics data
      if (metrics.some(m => typeof m.value !== 'number')) {
        console.error('Invalid metric value type:', metrics.filter(m => typeof m.value !== 'number'));
        setError('Invalid metric data');
      }
    } catch (err) {
      console.error('Error in MetricsPanel:', err);
      setError('Error processing metrics');
    }
  }, [metrics]);

  // Normalize floor ID formats
  const normalizeFloorId = (id: string): string => {
    // Handle different possible formats
    if (id.includes(' ')) {
      // Convert "1 East" to "1_east"
      const [number, wing] = id.split(' ');
      return `${number}_${wing.toLowerCase()}`;
    } else if (id.includes('_')) {
      // Already in correct format "1_east"
      return id.toLowerCase();
    } else {
      // Handle compact format "1E" to "1_east"
      const number = id.match(/\d+/)?.[0];
      const wing = id.match(/[A-Za-z]+/)?.[0];
      if (number && wing) {
        return `${number}_${wing.toLowerCase()}`;
      }
    }
    console.warn('Unable to normalize floor ID:', id);
    return id;
  };

  // Convert display floor name to floor_id format
  const getFloorId = (displayName: string) => {
    const normalized = normalizeFloorId(displayName);
    console.log('Normalized floor ID:', {
      original: displayName,
      normalized
    });
    return normalized;
  };

  // Filter metrics for the current floor and selected metrics
  const filteredMetrics = useMemo(() => {
    if (!displayFloor) return [];
    
    return metrics.filter(metric => 
      // Only show floor-level metrics
      metric.metric_type === 'floor' && 
      // Filter by selected categories
      selectedCategories.includes(metric.metric_category) &&
      // Filter by selected metrics
      selectedMetrics.includes(metric.metric_name) &&
      // Filter by current floor
      normalizeFloorId(metric.floor_id) === getFloorId(displayFloor)
    );
  }, [metrics, selectedCategories, selectedMetrics, displayFloor]);

  // Group metrics by category
  const metricGroups = useMemo(() => {
    const groups: MetricGroups = {
      'Patient Metrics': [],
      'Staff Metrics': []
    };

    filteredMetrics.forEach(metric => {
      if (selectedCategories.includes(metric.metric_category)) {
        groups[metric.metric_category].push(metric);
      }
    });

    return groups;
  }, [filteredMetrics, selectedCategories]);

  // Format metric value with units
  const formatValue = (value: number, metric: string): string => {
    let formattedValue = value.toFixed(1);
    let unit = '';

    switch (metric) {
      case 'occupancy':
        unit = '%';
        break;
      case 'staff_ratio':
        unit = ':1';
        break;
      default:
        unit = '';
    }

    return `${formattedValue}${unit}`;
  };

  const formatMetricName = (name: string): string => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getMetricUnit = (metricName: string): string => {
    if (metricName.includes('time')) return 'min';
    if (metricName.includes('satisfaction') || 
        metricName.includes('retention') || 
        metricName.includes('utilization') ||
        metricName.includes('rate')) return '%';
    if (metricName.includes('count') || 
        metricName.includes('total')) return '';
    return '';
  };

  const formatMetricValue = (value: number, metricName: string): string => {
    const unit = getMetricUnit(metricName);
    let formattedValue: string;

    if (value >= 100) {
      formattedValue = value.toFixed(0);
    } else if (value >= 10) {
      formattedValue = value.toFixed(1);
    } else {
      formattedValue = value.toFixed(2);
    }

    return `${formattedValue}${unit}`;
  };

  if (!displayFloor || !isVisible) {
    return null;
  }

  if (error) {
    return (
      <Card className="fixed top-4 right-4 w-80 shadow-lg bg-red-50">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-semibold text-red-600">Error</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-500">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={cn(
        'fixed top-4 right-4 w-80 shadow-lg transition-opacity duration-300 z-50',
        isHovered ? 'opacity-100' : 'opacity-90'
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle className="text-lg font-semibold">
            {displayFloor} Metrics
          </CardTitle>
          {showFloorDetail && onClose && (
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={onClose}
            >
              ×
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {selectedCategories.length === 0 ? (
          <p className="text-sm text-muted-foreground">No categories selected</p>
        ) : filteredMetrics.length === 0 ? (
          <p className="text-sm text-muted-foreground">No metrics available</p>
        ) : (
          selectedCategories.map((category) => (
            metricGroups[category]?.length > 0 && (
              <div key={category} className="mb-4">
                <h3 className="text-sm font-semibold mb-2">{category}</h3>
                {metricGroups[category].map((metric) => (
                  <div
                    key={`${metric.metric_name}-${metric.room_id || 'floor'}`}
                    className="flex justify-between items-center mb-1"
                  >
                    <span className="text-sm text-muted-foreground">
                      {formatMetricName(metric.metric_name)}
                      {metric.room_id && ` (${metric.room_id})`}
                    </span>
                    <span className="text-sm font-medium">
                      {formatMetricValue(metric.value, metric.metric_name)}
                    </span>
                  </div>
                ))}
              </div>
            )
          ))
        )}
      </CardContent>
    </Card>
  );
}

export default MetricsPanel;