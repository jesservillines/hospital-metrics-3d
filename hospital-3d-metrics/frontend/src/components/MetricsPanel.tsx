// MetricsPanel.tsx
import React, { useState, useEffect } from 'react';
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
  'Room Metrics': Metric[];
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
  const displayFloor = selectedFloor || hoveredFloor;

  useEffect(() => {
    if (hoveredFloor || selectedFloor) {
      setIsVisible(true);
    } else {
      const timer = setTimeout(() => setIsVisible(false), 300);
      return () => clearTimeout(timer);
    }
  }, [hoveredFloor, selectedFloor]);

  if (!displayFloor || !isVisible) {
    return null;
  }

  // Convert display floor name to floor_id format
  const getFloorId = (displayName: string) => {
    const [number, wing] = displayName.split(' ');
    return `${number}_${wing.toLowerCase()}`;
  };

  // Filter metrics for the current floor and selected metrics
  const floorMetrics = metrics.filter(m =>
    m.floor_id === getFloorId(displayFloor) &&
    selectedMetrics.includes(m.metric_name) &&
    m.metric_type === 'floor'
  );

  // Group metrics by category
  const groupMetricsByCategory = (metrics: Metric[]): MetricGroups => {
    const groups: MetricGroups = {
      'Patient Metrics': [],
      'Staff Metrics': [],
      'Room Metrics': []
    };

    metrics.forEach(metric => {
      // Use the metric_category from the backend
      const category = `${metric.metric_category.charAt(0).toUpperCase()}${metric.metric_category.slice(1)} Metrics`;
      
      if (selectedCategories.includes(category)) {
        groups[category].push(metric);
      }
    });

    return groups;
  };

  const formatMetricName = (name: string): string => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatMetricValue = (value: number): string => {
    if (value >= 100) {
      return value.toFixed(0);
    } else if (value >= 10) {
      return value.toFixed(1);
    }
    return value.toFixed(2);
  };

  const metricGroups = groupMetricsByCategory(floorMetrics);

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
        {selectedCategories.map((category) => (
          metricGroups[category]?.length > 0 && (
            <div key={category} className="mb-4">
              <h3 className="text-sm font-semibold mb-2">{category}</h3>
              {metricGroups[category].map((metric) => (
                <div
                  key={metric.metric_name}
                  className="flex justify-between items-center mb-1"
                >
                  <span className="text-sm text-muted-foreground">
                    {formatMetricName(metric.metric_name)}
                  </span>
                  <span className="text-sm font-medium">
                    {formatMetricValue(metric.value)}
                  </span>
                </div>
              ))}
            </div>
          )
        ))}
      </CardContent>
    </Card>
  );
}

export default MetricsPanel;