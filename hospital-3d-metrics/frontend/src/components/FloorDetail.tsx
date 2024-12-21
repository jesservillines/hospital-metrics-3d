// frontend/src/components/FloorDetail.tsx
import { useMemo } from 'react';
import * as THREE from 'three';
import FloorLayout from './FloorLayout';
import { Room } from '../services/roomDataService';
import type { RoomDataService } from '../services/roomDataService';

interface RoomData {
  room_id: string;
  room_type: string;
  room_name: string;
  width: number;
  depth: number;
  x_position: number;
  z_position: number;
  notes?: string;
}

interface FloorDetailProps {
  floorName: string;
  onClose: () => void;
  metrics: any[];
  selectedMetric: string;
  roomsData: any;
  selectedColor: string;
}

export function FloorDetail({
  floorName,
  onClose,
  metrics,
  selectedMetric,
  roomsData,
  selectedColor
}: FloorDetailProps) {
  // Get floor data using the service's getFloor method
  const floorRooms = useMemo(() => {
    try {
      const floorData = roomsData.getFloor(floorName);
      if (!floorData) {
        console.warn('No floor data found for:', floorName);
        return [];
      }
      console.log('Floor data loaded:', floorData);
      return floorData.rooms || [];
    } catch (error) {
      console.error('Error getting floor data:', error);
      return [];
    }
  }, [roomsData, floorName]);

  const metricValues = useMemo(() => {
    return metrics.filter((metric) => metric.floor === floorName && metric.room).map((metric) => metric.value);
  }, [metrics, floorName]);

  const getColorForValue = (value: number) => {
    const minValue = Math.min(...metricValues);
    const maxValue = Math.max(...metricValues);
    const normalizedValue = (value - minValue) / (maxValue - minValue);
    
    // Convert the selected color to RGB
    const color = new THREE.Color(selectedColor);
    const { r, g, b } = color;
    
    // Create a gradient from white to the selected color
    return new THREE.Color(
      1 - normalizedValue * (1 - r),
      1 - normalizedValue * (1 - g),
      1 - normalizedValue * (1 - b)
    );
  };

  return (
    <group>
      {/* Base floor plane */}
      <mesh
        position={[0, -0.1, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        receiveShadow
      >
        <planeGeometry args={[100, 60]} />
        <meshStandardMaterial color="#f0f0f0" />
      </mesh>

      {/* Loading state when no rooms are available */}
      {floorRooms.length === 0 ? (
        <group position={[0, 2, 0]}>
          <mesh>
            <boxGeometry args={[2, 2, 2]} />
            <meshStandardMaterial color="#cccccc" />
          </mesh>
        </group>
      ) : (
        <group position={[0, 0, 0]}>
          <FloorLayout
            floorName={floorName}
            rooms={floorRooms}
            selectedMetric={selectedMetric}
            metrics={metrics}
            onRoomSelect={(room) => {
              console.log('Selected room:', room);
            }}
            getColorForValue={getColorForValue}
          />
        </group>
      )}
    </group>
  );
}

export default FloorDetail;