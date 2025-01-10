import { useMemo } from 'react';
import * as THREE from 'three';
import { Vector3, Euler } from 'three';
import { createColorScale, getMetricValue } from '../utils/colorUtils';

interface BuildingProps {
  name: string;
  position: Vector3 | [number, number, number];
  width: number;
  height: number;
  depth: number;
  floorCount: number;
  floorHeight: number;
  onHoverFloor: (floor: string | null) => void;
  onSelectFloor: (floor: string | null) => void;
  hoveredFloor: string | null;
  selectedFloor: string | null;
  selectedColor: string;
  metrics: Array<{
    floor_id: string;
    room_id?: string;
    metric_name: string;
    value: number;
    timestamp: string;
    metric_type: 'floor' | 'room';
  }>;
  selectedMetric: string;
  rotation?: [number, number, number];
}

export function Building({
  name,
  position,
  width,
  height,
  depth,
  floorCount,
  floorHeight,
  onHoverFloor,
  onSelectFloor,
  hoveredFloor,
  selectedFloor,
  selectedColor,
  metrics,
  selectedMetric,
  rotation = [0, 0, 0]
}: BuildingProps) {
  const floors = useMemo(() => {
    const floorGeometry = new THREE.BoxGeometry(width, floorHeight, depth);
    const floors = [];

    // Filter metrics for the selected metric type only
    const relevantMetrics = metrics.filter(m => 
      m.metric_name === selectedMetric && 
      m.metric_type === 'floor'
    );
    const metricValues = relevantMetrics.map(m => m.value);

    // Create color scale only if we have values
    const getColor = metricValues.length > 0
      ? createColorScale(metricValues, selectedColor)
      : null;

    // Debug logging
    console.log('Building metrics:', {
      name,
      selectedMetric,
      metricValues,
      relevantMetrics,
      selectedColor
    });

    for (let i = 0; i < floorCount; i++) {
      const floorNumber = i + 1;
      const floorId = `${floorNumber}_${name.toLowerCase()}`;
      const displayName = `${floorNumber} ${name}`;
      const isHovered = hoveredFloor === displayName;
      const isSelected = selectedFloor === displayName;
      const floorY = (i * floorHeight) + (floorHeight / 2);

      // Get the metric value for this floor
      const value = getMetricValue(metrics, floorId, selectedMetric, 'floor');

      // Determine floor color
      let floorColor = '#ffffff';
      if (isSelected) {
        floorColor = selectedColor;
      } else if (value !== undefined && getColor) {
        floorColor = '#' + getColor(value);
        console.log(`Floor ${displayName} color:`, floorColor, 'value:', value);
      }

      floors.push(
        <mesh
          key={floorId}
          position={[0, floorY, 0]}
          geometry={floorGeometry}
          onPointerOver={(e) => {
            e.stopPropagation();
            onHoverFloor(displayName);
          }}
          onPointerOut={() => onHoverFloor(null)}
          onClick={(e) => {
            e.stopPropagation();
            onSelectFloor(isSelected ? null : displayName);
          }}
          castShadow
          receiveShadow
        >
          <meshStandardMaterial
            color={floorColor}
            transparent={true}
            opacity={isHovered ? 0.8 : 1}
            metalness={0.1}
            roughness={0.8}
          />
        </mesh>
      );
    }

    return floors;
  }, [
    width,
    floorHeight,
    depth,
    floorCount,
    hoveredFloor,
    selectedFloor,
    selectedColor,
    metrics,
    selectedMetric,
    onHoverFloor,
    onSelectFloor,
    name
  ]);

  return (
    <group
      position={position instanceof Vector3 ? position : new Vector3(...position)}
      rotation={new Euler(...rotation)}
    >
      {floors}
    </group>
  );
}

export default Building;