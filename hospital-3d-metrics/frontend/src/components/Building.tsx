// frontend/src/components/Building.tsx
import { useEffect, useMemo } from 'react'
import * as THREE from 'three'
import { Vector3, Euler } from 'three'
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
  // Generate floors with heatmap coloring
  const floors = useMemo(() => {
    const floorGeometry = new THREE.BoxGeometry(width, floorHeight, depth);
    const floors = [];

    // Get all metric values for the selected metric
    const metricValues = metrics
      .filter(m => m.metric_name === selectedMetric)
      .map(m => m.value);

    // Create color scale if we have values
    const colorScale = metricValues.length > 0
      ? getColorScale(metricValues)
      : null;

    for (let i = 0; i < floorCount; i++) {
      const floorName = `${i + 1} ${name}`;
      const isHovered = hoveredFloor === floorName;
      const isSelected = selectedFloor === floorName;
      const floorY = (i * floorHeight) + (floorHeight / 2);

      // Find this floor's metric value
      const floorMetric = metrics.find(
        m => m.floor === floorName && m.metric_name === selectedMetric
      );

      // Determine floor color
      let floorColor = '#ffffff'; // Default white
      if (isSelected) {
        floorColor = selectedColor;
      } else if (floorMetric && colorScale) {
        floorColor = colorScale(floorMetric.value);
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
    <group position={position instanceof THREE.Vector3 ? position : new THREE.Vector3(...position)} rotation={new THREE.Euler(...rotation)}>
      {floors}
    </group>
  );
};