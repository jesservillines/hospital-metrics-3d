import { useMemo } from 'react';
import * as THREE from 'three';
import { Vector3, Euler } from 'three';
import { getColorScale } from '../utils/colorScales';

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
    floor: string;
    metric_name: string;
    value: number;
    timestamp: string;
  }>;
  selectedMetric: string;
  rotation?: [number, number, number];
}

export const Building = ({
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
}: BuildingProps) => {
  const floors = useMemo(() => {
    const floorGeometry = new THREE.BoxGeometry(width, floorHeight, depth);
    const floors = [];

    // Filter metrics for the selected metric type only
    const relevantMetrics = metrics.filter(m => m.metric_name === selectedMetric);
    const metricValues = relevantMetrics.map(m => m.value);

    // Create color scale only if we have values
    const colorScale = metricValues.length > 0
      ? getColorScale(metricValues)
      : null;

    // Debug logging
    console.log('Building metrics:', {
      name,
      selectedMetric,
      metricValues,
      relevantMetrics
    });

    for (let i = 0; i < floorCount; i++) {
      const floorName = `${i + 1} ${name}`;
      const isHovered = hoveredFloor === floorName;
      const isSelected = selectedFloor === floorName;
      const floorY = (i * floorHeight) + (floorHeight / 2);

      // Find the metric for this floor
      const floorMetric = relevantMetrics.find(m => m.floor === floorName);

      // Determine floor color
      let floorColor = '#ffffff';
      if (isSelected) {
        floorColor = selectedColor;
      } else if (floorMetric && colorScale) {
        floorColor = colorScale(floorMetric.value);
        console.log(`Floor ${floorName} color:`, floorColor, 'value:', floorMetric.value);
      }

      floors.push(
        <mesh
          key={floorName}
          position={[0, floorY, 0]}
          geometry={floorGeometry}
          onPointerOver={(e) => {
            e.stopPropagation();
            onHoverFloor(floorName);
          }}
          onPointerOut={() => onHoverFloor(null)}
          onClick={(e) => {
            e.stopPropagation();
            onSelectFloor(isSelected ? null : floorName);
          }}
          castShadow
          receiveShadow
        >
          <meshStandardMaterial
            color={floorColor}
            transparent
            opacity={isHovered ? 0.9 : 0.8}
          />
        </mesh>
      );
    }
    return floors;
  }, [
    name, width, height, depth, floorCount, floorHeight,
    hoveredFloor, selectedFloor, selectedColor, metrics,
    selectedMetric, onHoverFloor, onSelectFloor
  ]);

  return (
    <group
      position={position instanceof THREE.Vector3 ? position : new THREE.Vector3(...position)}
      rotation={new THREE.Euler(...rotation)}
    >
      {floors}
    </group>
  );
};