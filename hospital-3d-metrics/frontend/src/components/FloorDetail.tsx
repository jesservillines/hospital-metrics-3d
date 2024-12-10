import { useMemo } from 'react';
import * as THREE from 'three';
import { FloorLayout } from './FloorLayout';
import { Room } from '../services/roomDataService';

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
  roomsData: {
    rooms: Room[];
  };
}

export const FloorDetail: React.FC<FloorDetailProps> = ({
  floorName,
  onClose,
  metrics,
  selectedMetric,
  roomsData
}) => {
  // Debug logging
  console.log('FloorDetail Props:', {
    floorName,
    metricsCount: metrics?.length,
    selectedMetric,
    roomsCount: roomsData?.rooms?.length
  });

  const floorRooms = useMemo(() => {
    if (!roomsData?.rooms) {
      console.warn('No room data available for floor:', floorName);
      return [];
    }

    // Transform room data to match Room interface
    const transformedRooms = roomsData.rooms.map(room => ({
      id: room.id,
      floor: floorName,
      type: room.type,
      name: room.name,
      width: room.width,
      depth: room.depth,
      x_position: room.x_position,
      z_position: room.z_position,
      properties: room.properties,
      metrics: room.metrics
    }));

    console.log('Transformed rooms:', transformedRooms);
    return transformedRooms;
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

      {/* Render the floor layout if we have rooms */}
      {floorRooms.length > 0 ? (
        <FloorLayout
          floorName={floorName}
          rooms={floorRooms}
          selectedMetric={selectedMetric}
          metrics={metrics}
          onRoomSelect={(room) => {
            console.log('Selected room:', room);
          }}
        />
      ) : (
        <mesh position={[0, 1, 0]}>
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial color="red" />
        </mesh>
      )}
    </group>
  );
};