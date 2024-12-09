import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface Metric {
  floor: string;
  room?: string;
  metric_name: string;
  value: number;
  timestamp: string;
  metric_type: string;
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

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  hoveredFloor,
  selectedFloor,
  metrics,
  selectedCategories,
  selectedMetrics,
  showFloorDetail = false,
  onClose
}) => {
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

  // Filter metrics for the current floor and selected metrics
  const floorMetrics = metrics.filter(m =>
    m.floor === displayFloor &&
    selectedMetrics.includes(m.metric_name) &&
    m.metric_type === 'floor'
  );

  console.log('Filtered floor metrics:', floorMetrics);

  // Group metrics by category
  const groupMetricsByCategory = (metrics: Metric[]): MetricGroups => {
    const groups: MetricGroups = {
      'Patient Metrics': [],
      'Staff Metrics': [],
      'Room Metrics': []
    };

    metrics.forEach(metric => {
      let category: string;
      const metricName = metric.metric_name.toLowerCase();

      if (metricName.includes('patient') ||
          metricName.includes('fall') ||
          metricName.includes('therapy')) {
        category = 'Patient Metrics';
      } else if (metricName.includes('staff') ||
                 metricName.includes('nurse') ||
                 metricName.includes('retention')) {
        category = 'Staff Metrics';
      } else {
        category = 'Room Metrics';
      }

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

  const formatMetricValue = (metric: Metric): string => {
    const value = metric.value;
    const name = metric.metric_name.toLowerCase();

    if (name.includes('time')) {
      return `${value.toFixed(1)} min`;
    } else if (name.includes('temperature')) {
      return `${value.toFixed(1)}°F`;
    } else if (name.includes('humidity')) {
      return `${value.toFixed(1)}%`;
    } else if (name.includes('count') || name.includes('total')) {
      return value.toFixed(0);
    } else {
      return `${value.toFixed(1)}%`;
    }
  };

  const getMetricColor = (metricName: string): string => {
    const name = metricName.toLowerCase();
    if (name.includes('risk')) {
      return 'bg-red-500';
    } else if (name.includes('satisfaction') || name.includes('completion')) {
      return 'bg-green-500';
    } else {
      return 'bg-craig-blue';
    }
  };

  const getMetricProgress = (metric: Metric): number => {
    const value = metric.value;
    if (metric.metric_name.includes('risk')) {
      return Math.min(value, 100); // Risk metrics should still show as percentage
    }
    return Math.min(value, 100); // Ensure value doesn't exceed 100%
  };

  const groupedMetrics = groupMetricsByCategory(floorMetrics);

  return (
    <div
      className={cn(
        "absolute right-4 top-4 w-80 z-10",
        showFloorDetail ? "opacity-100" : isHovered ? "opacity-100" : "opacity-75",
        "transition-opacity duration-300"
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Card className="relative bg-opacity-90 bg-white border border-white/20 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Floor {displayFloor} Metrics</CardTitle>
          {showFloorDetail && onClose && (
            <Button
              variant="ghost"
              onClick={onClose}
              className="text-sm font-medium"
            >
              Back to Overview
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {Object.entries(groupedMetrics)
              .filter(([category]) => selectedCategories.includes(category))
              .map(([category, categoryMetrics]) => {
                if (categoryMetrics.length === 0) return null;

                return (
                  <div key={category} className="space-y-4">
                    <h3 className="font-semibold text-sm text-gray-500">{category}</h3>
                    {categoryMetrics.map((metric) => (
                      <div key={metric.metric_name} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="font-medium">
                            {formatMetricName(metric.metric_name)}
                          </span>
                          <span className="font-semibold">
                            {formatMetricValue(metric)}
                          </span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={cn(
                              "h-full rounded-full transition-all duration-300",
                              getMetricColor(metric.metric_name)
                            )}
                            style={{
                              width: `${getMetricProgress(metric)}%`,
                              opacity: metric.metric_name.includes('risk') ? 0.7 : 1
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                );
              })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};