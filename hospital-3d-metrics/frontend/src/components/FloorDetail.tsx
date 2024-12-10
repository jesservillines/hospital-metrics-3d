// frontend/src/components/FloorDetail.tsx
import { useMemo } from 'react';
import * as THREE from 'three';
import { FloorLayout } from './FloorLayout';
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
  metrics: Array<{
    floor: string;
    room?: string;
    metric_name: string;
    value: number;
    timestamp: string;
    metric_type: string;
  }>;
  selectedMetric: string;
  roomsData: RoomDataService;
}

export const FloorDetail: React.FC<FloorDetailProps> = ({
  floorName,
  onClose,
  metrics,
  selectedMetric,
  roomsData
}) => {
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
          />
        </group>
      )}
    </group>
  );
};