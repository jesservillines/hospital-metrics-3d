// frontend/src/components/MetricsPanel.tsx
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

interface MetricsPanelProps {
  selectedFloor: string | null;
  metrics: any[];
}

export const MetricsPanel: React.FC<MetricsPanelProps> = ({ selectedFloor, metrics }) => {
  if (!selectedFloor) {
    return null;
  }

  const floorMetrics = metrics.filter(m => m.floor === selectedFloor);

  return (
    <Card className="absolute right-4 top-4 w-80 bg-white/90 backdrop-blur">
      <CardHeader>
        <CardTitle>Floor {selectedFloor} Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {floorMetrics.map((metric) => (
            <div key={metric.metric_name} className="space-y-2">
              <div className="flex justify-between">
                <span className="font-medium">{metric.metric_name}</span>
                <span>{metric.value.toFixed(1)}</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{ width: `${(metric.value / 100) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};