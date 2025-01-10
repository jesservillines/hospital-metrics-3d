import * as THREE from 'three';

export function createColorScale(values: number[], baseColor: string) {
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const range = maxValue - minValue;

  // Convert the base color to RGB
  const color = new THREE.Color(baseColor);
  const { r, g, b } = color;

  return (value: number) => {
    // Normalize the value between 0 and 1
    const normalizedValue = range === 0 ? 1 : (value - minValue) / range;
    
    // Create a gradient from white to the base color
    return new THREE.Color(
      1 - normalizedValue * (1 - r),
      1 - normalizedValue * (1 - g),
      1 - normalizedValue * (1 - b)
    ).getHexString();
  };
}

export function getMetricValue(
  metrics: any[],
  id: string,
  selectedMetric: string,
  type: 'floor' | 'room'
) {
  const metric = metrics.find(m => 
    m.metric_name === selectedMetric && 
    (type === 'floor' ? m.floor_id === id : m.room_id === id)
  );
  return metric?.value;
}
