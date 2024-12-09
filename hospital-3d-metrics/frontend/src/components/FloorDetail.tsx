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

  // Log the actual metrics and room data
  console.log('Metrics:', metrics);
  console.log('Rooms Data:', roomsData);

  const floorRooms = useMemo(() => {
    if (!roomsData?.rooms) {
      console.warn('No room data available for floor:', floorName);
      return [];
    }

    // Transform room data to match Room interface
    return roomsData.rooms.map(room => ({
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
  }, [roomsData, floorName]);

  // Early return if no data
  if (!floorRooms.length) {
    console.warn('No rooms to display for floor:', floorName);
    return null;
  }

  console.log('Processed floor rooms:', floorRooms);

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
  );
};