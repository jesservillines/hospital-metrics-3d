// frontend/src/components/FloorDetail.tsx
import { useMemo } from 'react';
import * as THREE from 'three';
import { Text, Billboard } from '@react-three/drei';
import { getColorScale } from '../utils/colorScales';

interface Room {
  id: string;
  type: 'patient' | 'therapy' | 'office';
  name: string;
  width: number;
  depth: number;
  position: [number, number, number];
  metrics?: {
    [key: string]: number;
  };
}

interface RoomRowConfig {
  startX: number;
  y: number;
  z: number;
  roomCount: number;
  roomType: 'patient' | 'therapy' | 'office';
  roomWidth: number;
  roomDepth: number;
  spacing: number;
  rowIdentifier: string;
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
}

const Room: React.FC<{
  room: Room;
  onClick: (room: Room) => void;
  color: string;
  opacity: number;
}> = ({ room, onClick, color, opacity }) => {
  return (
    <group position={new THREE.Vector3(...room.position)}>
      <mesh
        onClick={() => onClick(room)}
        castShadow
        receiveShadow
        position={[0, 1.25, 0]}
      >
        <boxGeometry args={[room.width, 2.5, room.depth]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={opacity}
        />
      </mesh>

      <Billboard>
        <Text
          position={[0, 3.5, 0]}
          fontSize={0.5}
          color="black"
          anchorX="center"
          anchorY="middle"
        >
          {room.name}
        </Text>
      </Billboard>
    </group>
  );
};

export const FloorDetail: React.FC<FloorDetailProps> = ({
  floorName,
  onClose,
  metrics,
  selectedMetric
}) => {
  const BASE_Y = 0;

  const generateRooms = (config: RoomRowConfig): Room[] => {
    const rooms: Room[] = [];
    const { startX, y, z, roomCount, roomType, roomWidth, roomDepth, spacing, rowIdentifier } = config;

    for (let i = 0; i < roomCount; i++) {
      const x = startX + (i * (roomWidth + spacing));
      const uniqueId = `${floorName}-${rowIdentifier}-${roomType}-${i + 1}`;
      rooms.push({
        id: uniqueId,
        type: roomType,
        name: `${roomType.charAt(0).toUpperCase() + roomType.slice(1)} ${i + 1}`,
        width: roomWidth,
        depth: roomDepth,
        position: [x, y, z],
        metrics: {
          occupancy: Math.random() * 100,
          satisfaction: Math.floor(Math.random() * 100),
        },
      });
    }
    return rooms;
  };

  const rooms = useMemo(() => {
    const configs = {
      patientRow1: {
        startX: -15,
        y: BASE_Y,
        z: -8,
        roomCount: 6,
        roomType: 'patient' as const,
        roomWidth: 4,
        roomDepth: 3,
        spacing: 1,
        rowIdentifier: 'row1'
      },
      patientRow2: {
        startX: -15,
        y: BASE_Y,
        z: 8,
        roomCount: 6,
        roomType: 'patient' as const,
        roomWidth: 4,
        roomDepth: 3,
        spacing: 1,
        rowIdentifier: 'row2'
      },
      therapy: {
        startX: -12,
        y: BASE_Y,
        z: 0,
        roomCount: 4,
        roomType: 'therapy' as const,
        roomWidth: 6,
        roomDepth: 4,
        spacing: 2,
        rowIdentifier: 'therapy'
      },
      office: {
        startX: 10,
        y: BASE_Y,
        z: 0,
        roomCount: 3,
        roomType: 'office' as const,
        roomWidth: 5,
        roomDepth: 4,
        spacing: 1,
        rowIdentifier: 'office'
      },
    };

    return Object.entries(configs).flatMap(([_, config]) =>
      generateRooms(config)
    );
  }, [floorName]);

  const roomMetrics = useMemo(() => {
    return metrics.filter(m =>
      m.metric_type === 'room' &&
      m.metric_name === selectedMetric &&
      m.floor === floorName
    );
  }, [metrics, selectedMetric, floorName]);

  const colorScale = useMemo(() => {
    const values = roomMetrics.map(m => m.value);
    return getColorScale(values);
  }, [roomMetrics]);

  const getRoomColor = (room: Room) => {
    const baseColors = {
      patient: '#90cdf4',
      therapy: '#9ae6b4',
      office: '#fbd38d',
    };

    const metric = roomMetrics.find(m => m.room === room.name);
    return metric ? colorScale(metric.value) : baseColors[room.type];
  };

  const handleRoomClick = (room: Room) => {
    const metric = roomMetrics.find(m => m.room === room.name);
    console.log('Room clicked:', room, 'Metric:', metric);
  };

  return (
    <group>
      <group position={[0, BASE_Y, 0]}>
        <mesh
          receiveShadow
          position={[0, -0.1, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
        >
          <planeGeometry args={[50, 30]} />
          <meshStandardMaterial
            color="#e2e8f0"
            roughness={0.8}
            metalness={0.2}
          />
        </mesh>

        <mesh position={[0, -0.2, 0]}>
          <boxGeometry args={[50, 0.2, 30]} />
          <meshStandardMaterial color="#cbd5e0" />
        </mesh>

        <mesh
          position={[0, 0, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
        >
          <planeGeometry args={[40, 3]} />
          <meshStandardMaterial
            color="#cbd5e0"
            roughness={0.7}
          />
        </mesh>
      </group>

      {rooms.map((room) => (
        <Room
          key={room.id}
          room={room}
          onClick={handleRoomClick}
          color={getRoomColor(room)}
          opacity={0.8}
        />
      ))}

      <Billboard>
        <Text
          position={[0, 5, -12]}
          fontSize={2}
          color="black"
          anchorX="center"
          anchorY="middle"
        >
          {floorName}
        </Text>
      </Billboard>
    </group>
  );
};