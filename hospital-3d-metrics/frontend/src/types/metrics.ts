export interface MetricOption {
  value: string;
  label: string;
}

export interface Metric {
  floor_id: string;
  room_id?: string;
  metric_name: string;
  value: number;
  timestamp: string;
  metric_type: 'floor' | 'room';
  metric_category: string;
}

export interface MetricGroups {
  [category: string]: Metric[];
}

export interface MetricDefinition {
  name: string;
  display_name: string;
  category: string;
  data_type: string;
  description: string;
  units?: string;
  aggregation_type?: string;
}

export interface AvailableMetrics {
  categories: string[];
  metrics: MetricDefinition[];
}
