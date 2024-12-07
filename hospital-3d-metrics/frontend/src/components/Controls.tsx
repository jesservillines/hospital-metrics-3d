// frontend/src/components/Controls.tsx
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Select } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';

interface ControlsProps {
  onMetricChange: (metric: string) => void;
  onDateRangeChange: (range: [Date, Date]) => void;
  metrics: string[];
}

export const Controls: React.FC<ControlsProps> = ({
  onMetricChange,
  onDateRangeChange,
  metrics,
}) => {
  return (
    <Card className="absolute left-4 top-4 w-80 bg-white/90 backdrop-blur">
      <CardHeader>
        <CardTitle>Controls</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Metric</label>
            <Select
              onValueChange={onMetricChange}
              options={metrics.map(m => ({ value: m, label: m }))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Date Range</label>
            <Slider
              defaultValue={[0, 100]}
              max={100}
              step={1}
              onValueChange={(values) => {
                // Convert slider values to dates
                const start = new Date();
                const end = new Date();
                start.setDate(start.getDate() - values[0]);
                end.setDate(end.getDate() - values[1]);
                onDateRangeChange([start, end]);
              }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};