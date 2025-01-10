import { render, screen } from '@testing-library/react';
import { MetricsPanel } from '../components/MetricsPanel';
import { vi } from 'vitest';

describe('MetricsPanel', () => {
  const mockMetrics = [
    {
      floor_id: '1_east',
      metric_name: 'patient_satisfaction',
      value: 85.5,
      timestamp: '2024-01-01T00:00:00Z',
      metric_category: 'Patient Metrics',
      metric_type: 'floor'
    },
    {
      floor_id: '1_east',
      metric_name: 'staff_retention',
      value: 90.0,
      timestamp: '2024-01-01T00:00:00Z',
      metric_category: 'Staff Metrics',
      metric_type: 'floor'
    },
    {
      floor_id: '1_east',
      room_id: 'room_101',
      metric_name: 'room_occupancy',
      value: 75.0,
      timestamp: '2024-01-01T00:00:00Z',
      metric_category: 'Room Metrics',
      metric_type: 'room'
    }
  ];

  it('should display metrics when floor is hovered', () => {
    render(
      <MetricsPanel
        hoveredFloor="1 East"
        selectedFloor={null}
        metrics={mockMetrics}
        selectedCategories={['Patient Metrics', 'Staff Metrics']}
        selectedMetrics={['patient_satisfaction', 'staff_retention']}
      />
    );

    // Check if metrics are displayed
    expect(screen.getByText('Patient Satisfaction')).toBeInTheDocument();
    expect(screen.getByText('85.5%')).toBeInTheDocument();
    expect(screen.getByText('Staff Retention')).toBeInTheDocument();
    expect(screen.getByText('90.0%')).toBeInTheDocument();
  });

  it('should not display metrics for unselected categories', () => {
    render(
      <MetricsPanel
        hoveredFloor="1 East"
        selectedFloor={null}
        metrics={mockMetrics}
        selectedCategories={['Patient Metrics']} // Only patient metrics
        selectedMetrics={['patient_satisfaction', 'staff_retention']}
      />
    );

    // Patient metrics should be visible
    expect(screen.getByText('Patient Satisfaction')).toBeInTheDocument();
    expect(screen.getByText('85.5%')).toBeInTheDocument();

    // Staff metrics should not be visible
    expect(screen.queryByText('Staff Retention')).not.toBeInTheDocument();
  });

  it('should handle floor_id conversion correctly', () => {
    const metricsWithDifferentFormat = [
      {
        floor_id: '2_west',
        metric_name: 'patient_satisfaction',
        value: 85.5,
        timestamp: '2024-01-01T00:00:00Z',
        metric_category: 'Patient Metrics',
        metric_type: 'floor'
      }
    ];

    render(
      <MetricsPanel
        hoveredFloor="2 West"
        selectedFloor={null}
        metrics={metricsWithDifferentFormat}
        selectedCategories={['Patient Metrics']}
        selectedMetrics={['patient_satisfaction']}
      />
    );

    // Check if metrics are displayed despite different floor_id format
    expect(screen.getByText('Patient Satisfaction')).toBeInTheDocument();
    expect(screen.getByText('85.5%')).toBeInTheDocument();
  });

  it('should handle empty metrics array', () => {
    render(
      <MetricsPanel
        hoveredFloor="1 East"
        selectedFloor={null}
        metrics={[]}
        selectedCategories={['Patient Metrics', 'Staff Metrics']}
        selectedMetrics={['patient_satisfaction', 'staff_retention']}
      />
    );

    // Panel should be visible but show no metrics
    expect(screen.getByText('1 East')).toBeInTheDocument();
    expect(screen.queryByText('Patient Satisfaction')).not.toBeInTheDocument();
  });

  it('should display room metrics when available', () => {
    render(
      <MetricsPanel
        hoveredFloor="1 East"
        selectedFloor={null}
        metrics={mockMetrics}
        selectedCategories={['Room Metrics']}
        selectedMetrics={['room_occupancy']}
      />
    );

    // Room metrics should be visible with room ID
    expect(screen.getByText('Room Occupancy (room_101)')).toBeInTheDocument();
    expect(screen.getByText('75.0%')).toBeInTheDocument();
  });

  it('should handle both floor and room metrics together', () => {
    render(
      <MetricsPanel
        hoveredFloor="1 East"
        selectedFloor={null}
        metrics={mockMetrics}
        selectedCategories={['Patient Metrics', 'Room Metrics']}
        selectedMetrics={['patient_satisfaction', 'room_occupancy']}
      />
    );

    // Both floor and room metrics should be visible
    expect(screen.getByText('Patient Satisfaction')).toBeInTheDocument();
    expect(screen.getByText('85.5%')).toBeInTheDocument();
    expect(screen.getByText('Room Occupancy (room_101)')).toBeInTheDocument();
    expect(screen.getByText('75.0%')).toBeInTheDocument();
  });

  it('should handle room metrics with missing room_id', () => {
    const metricsWithMissingRoomId = [
      {
        floor_id: '1_east',
        metric_name: 'room_occupancy',
        value: 75.0,
        timestamp: '2024-01-01T00:00:00Z',
        metric_category: 'Room Metrics',
        metric_type: 'room'
      }
    ];

    render(
      <MetricsPanel
        hoveredFloor="1 East"
        selectedFloor={null}
        metrics={metricsWithMissingRoomId}
        selectedCategories={['Room Metrics']}
        selectedMetrics={['room_occupancy']}
      />
    );

    // Should still display the metric without room ID
    expect(screen.getByText('Room Occupancy')).toBeInTheDocument();
    expect(screen.getByText('75.0%')).toBeInTheDocument();
  });
});
