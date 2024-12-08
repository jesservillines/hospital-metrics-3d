// frontend/src/components/MetricsPanel.tsx
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

interface MetricsPanelProps {
  hoveredFloor: string | null;
  selectedFloor: string | null;
  metrics: {
    floor: string;
    metric_name: string;
    value: number;
    timestamp: string;
  }[];
  selectedCategories: string[];
  selectedMetrics: string[];
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({
  hoveredFloor,
  selectedFloor,
  metrics,
  selectedCategories,
  selectedMetrics,
}) => {
  if (!hoveredFloor) {
    return null;
  }

  const floorMetrics = metrics.filter(m => m.floor === hoveredFloor);

  const metricGroups = {
    'Patient Metrics': ['patient_satisfaction', 'fall_risk'],
    'Staff Metrics': ['staff_retention']
  };

  const filteredGroups = Object.entries(metricGroups)
    .filter(([groupName]) => selectedCategories.includes(groupName))
    .reduce((acc, [groupName, metrics]) => ({
      ...acc,
      [groupName]: metrics.filter(metric => selectedMetrics.includes(metric))
    }), {} as Record<string, string[]>);

  return (
    <div className="absolute right-4 top-4 w-80 z-10">
      <Card className="relative bg-opacity-75 bg-white border border-white/20 backdrop-blur-sm">
        <CardHeader>
          <CardTitle>Floor {hoveredFloor} Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {Object.entries(filteredGroups).map(([groupName, metricNames]) => {
              if (metricNames.length === 0) return null;

              return (
                <div key={groupName} className="space-y-4">
                  <h3 className="font-semibold text-sm text-gray-500">{groupName}</h3>
                  {metricNames.map((metricName) => {
                    const metric = floorMetrics.find(m => m.metric_name === metricName);
                    if (!metric) return null;

                    return (
                      <div key={metricName} className="space-y-2">
                        <div className="flex justify-between">
                          <span className="font-medium">
                            {metricName.split('_').map(word =>
                              word.charAt(0).toUpperCase() + word.slice(1)
                            ).join(' ')}
                          </span>
                          <span className="font-semibold">{metric.value.toFixed(1)}%</span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-craig-blue rounded-full transition-all duration-300"
                            style={{
                              width: `${metric.value}%`,
                              opacity: metric.metric_name === 'fall_risk' ? 0.7 : 1
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};