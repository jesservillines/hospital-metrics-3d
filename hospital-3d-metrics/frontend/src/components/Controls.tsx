// frontend/src/components/Controls.tsx
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Check, ChevronsUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ControlsProps {
  onMetricChange: (metric: string) => void;
  onCategoryChange: (categories: string[]) => void;
  onMetricsSelectionChange: (metrics: string[]) => void;
  selectedMetric: string;
  selectedCategories: string[];
  selectedMetrics: string[];
}

export const Controls: React.FC<ControlsProps> = ({
  onMetricChange,
  onCategoryChange,
  onMetricsSelectionChange,
  selectedMetric,
  selectedCategories,
  selectedMetrics,
}) => {
  const [open, setOpen] = React.useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const metrics = [
    { value: 'patient_satisfaction', label: 'Patient Satisfaction', category: 'Patient Metrics' },
    { value: 'fall_risk', label: 'Fall Risk', category: 'Patient Metrics' },
    { value: 'staff_retention', label: 'Staff Retention', category: 'Staff Metrics' }
  ];

  const categories = [
    { id: 'patient-metrics', label: 'Patient Metrics' },
    { id: 'staff-metrics', label: 'Staff Metrics' },
  ];

  const availableMetrics = metrics.filter(metric =>
    selectedCategories.includes(metric.category)
  );

  const allMetricsSelected = availableMetrics.every(metric =>
    selectedMetrics.includes(metric.value)
  );

  const handleSelectAllToggle = () => {
    if (allMetricsSelected) {
      onMetricsSelectionChange([]);
    } else {
      const allMetricsInCategories = availableMetrics.map(m => m.value);
      onMetricsSelectionChange(allMetricsInCategories);
    }
    setOpen(false);
  };

  return (
    <div
      className="absolute left-4 top-4 w-80 z-10"
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      <Card className="relative bg-opacity-75 bg-white border border-white/20 backdrop-blur-sm">
        <CardHeader className="cursor-pointer">
          <CardTitle>Visualization Controls</CardTitle>
        </CardHeader>
        <CardContent
          className={cn(
            "space-y-6 overflow-hidden transition-all duration-300",
            isExpanded ? "opacity-100 max-h-[500px]" : "opacity-0 max-h-0"
          )}
        >
          <div className="space-y-2">
            <label className="text-sm font-medium">Metric Categories</label>
            <div className="grid gap-4">
              {categories.map((category) => (
                <div className="flex items-center space-x-2" key={category.id}>
                  <Checkbox
                    id={category.id}
                    checked={selectedCategories.includes(category.label)}
                    onCheckedChange={(checked) => {
                      if (checked !== "indeterminate") {
                        const newCategories = checked
                          ? [...selectedCategories, category.label]
                          : selectedCategories.filter(c => c !== category.label);
                        onCategoryChange(newCategories);
                      }
                    }}
                  />
                  <label
                    htmlFor={category.id}
                    className="text-sm font-medium leading-none cursor-pointer"
                  >
                    {category.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Heatmap Metric</label>
            <Select
              value={selectedMetric}
              onValueChange={onMetricChange}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select metric to display" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                {availableMetrics.map((metric) => (
                  <SelectItem key={metric.value} value={metric.value}>
                    {metric.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Displayed Metrics</label>
            <Popover open={open} onOpenChange={setOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={open}
                  className="w-full justify-between bg-white"
                >
                  {selectedMetrics.length > 0
                    ? `${selectedMetrics.length} selected`
                    : "Select metrics..."}
                  <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-[--radix-popover-trigger-width] p-0 bg-white">
                <Command>
                  <CommandInput placeholder="Search metrics..." />
                  <CommandEmpty>No metrics found.</CommandEmpty>
                  <CommandGroup>
                    <CommandItem
                      onSelect={handleSelectAllToggle}
                      className="font-medium text-blue-600"
                    >
                      {allMetricsSelected ? "Deselect All" : "Select All Available"}
                    </CommandItem>
                    {availableMetrics.map((metric) => (
                      <CommandItem
                        key={metric.value}
                        onSelect={() => {
                          const newSelection = selectedMetrics.includes(metric.value)
                            ? selectedMetrics.filter(m => m !== metric.value)
                            : [...selectedMetrics, metric.value];
                          onMetricsSelectionChange(newSelection);
                        }}
                      >
                        <Check
                          className={cn(
                            "mr-2 h-4 w-4",
                            selectedMetrics.includes(metric.value) ? "opacity-100" : "opacity-0"
                          )}
                        />
                        {metric.label}
                      </CommandItem>
                    ))}
                  </CommandGroup>
                </Command>
              </PopoverContent>
            </Popover>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};