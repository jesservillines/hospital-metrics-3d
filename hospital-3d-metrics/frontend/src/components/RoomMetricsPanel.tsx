import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { MetricOption } from '../types/metrics';

interface RoomMetricsPanelProps {
  selectedMetric: string;
  onMetricChange: (metric: string) => void;
  metricOptions: MetricOption[];
  selectedColor: string;
  onColorChange: (color: string) => void;
  isVisible: boolean;
}

const RoomMetricsPanel: React.FC<RoomMetricsPanelProps> = ({
  selectedMetric,
  onMetricChange,
  metricOptions,
  selectedColor,
  onColorChange,
  isVisible
}) => {
  if (!isVisible) return null;

  return (
    <Card className="fixed top-4 right-4 w-[300px] z-50">
      <CardHeader>
        <CardTitle>Room Metrics</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="text-sm font-medium">Metric</div>
          <Select value={selectedMetric} onValueChange={onMetricChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select metric" />
            </SelectTrigger>
            <SelectContent>
              {metricOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <div className="text-sm font-medium">Color</div>
          <Select value={selectedColor} onValueChange={onColorChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select color" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="#ff0000">Red</SelectItem>
              <SelectItem value="#00ff00">Green</SelectItem>
              <SelectItem value="#0000ff">Blue</SelectItem>
              <SelectItem value="#ffa500">Orange</SelectItem>
              <SelectItem value="#800080">Purple</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  );
};

export default RoomMetricsPanel;
