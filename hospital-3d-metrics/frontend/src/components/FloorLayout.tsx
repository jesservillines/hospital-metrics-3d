import { useMemo, useState } from 'react';
import * as THREE from 'three';
import { Text, Billboard, Html } from '@react-three/drei';
import { useSpring, animated } from '@react-spring/three';
import { getColorScale } from '../utils/colorScales';
import { Room } from '../services/roomDataService';
import RoomDetail from './RoomDetail';

const AnimatedMesh = animated(({ color, ...props }: any) => (
  <mesh {...props}>
    <boxGeometry args={[props.width || 1, props.height || 1, props.depth || 1]} />
    <meshStandardMaterial color={color} transparent opacity={props.opacity} />
  </mesh>
));

interface RoomMeshProps {
  room: Room;
  isSelected: boolean;
  isHovered: boolean;
  onClick: () => void;
  onPointerOver: () => void;
  onPointerOut: () => void;
  metricColor?: string;
  metrics?: Array<{
    metric_name: string;
    value: number;
  }>;
}

function RoomMesh({
  room,
  isSelected,
  isHovered,
  onClick,
  onPointerOver,
  onPointerOut,
  metricColor,
  metrics = []
}: RoomMeshProps) {
  const height = room.type === 'hallway' ? 0.5 : 3;
  const baseColor = metricColor || getRoomTypeColor(room.type);
  const labelHeight = height + 2;

  const { color, scale, y } = useSpring({
    color: isSelected ? '#ffd700' : isHovered ? '#fff5cc' : baseColor,
    scale: isHovered ? 1.05 : 1,
    y: isSelected ? height / 2 + 0.2 : height / 2,
    config: { tension: 170, friction: 26 }
  });

  return (
    <group position={[room.x_position, 0, room.z_position]}>
      <AnimatedMesh
        position-y={y}
        scale={scale}
        width={room.width}
        height={height}
        depth={room.depth}
        color={color}
        opacity={room.type === 'hallway' ? 0.4 : 0.8}
        onClick={onClick}
        onPointerOver={onPointerOver}
        onPointerOut={onPointerOut}
        castShadow
        receiveShadow
      />

      {room.type !== 'hallway' && (
        <Billboard>
          <group>
            <mesh position={[0, labelHeight, 0]}>
              <planeGeometry args={[5, 1.2]} />
              <meshBasicMaterial color="white" transparent opacity={0.6} />
            </mesh>
            <Text
              position={[0, labelHeight, 0.01]}
              fontSize={0.7}
              color="black"
              anchorX="center"
              anchorY="middle"
              outlineWidth={0.02}
              outlineColor="white"
              maxWidth={4.5}
              textAlign="center"
            >
              {`${room.name}\n${getFormattedRoomType(room.type)}`}
            </Text>
          </group>
        </Billboard>
      )}

      {isHovered && room.type !== 'hallway' && (
        <Html position={[0, height + 3, 0]} center>
          <div className="bg-white p-3 rounded shadow-lg text-sm min-w-[200px]">
            <h3 className="font-bold text-base mb-2">{room.name}</h3>
            <div className="grid grid-cols-2 gap-2">
              {getRelevantMetrics(room, metrics).map((metric, index) => (
                <React.Fragment key={index}>
                  <span className="text-gray-600">
                    {formatMetricName(metric.label)}:
                  </span>
                  <span className="font-medium">{formatMetricValue(metric.value, metric.label)}</span>
                </React.Fragment>
              ))}
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

function getRelevantMetrics(room: Room, metrics: Array<{ metric_name: string; value: number }>) {
  // Filter metrics based on room type from the metric_category field
  const relevantMetrics = metrics.filter(metric => {
    // The backend sends the category in the metric name or as a separate field
    // We'll display all metrics that are sent for this room
    return true;
  });

  return relevantMetrics.map(metric => ({
    label: metric.metric_name,
    value: metric.value
  }));
};

function getRoomTypeColor(type: Room['type']): string {
  const colors = {
    patient: '#90cdf4',   // Light blue
    therapy: '#9ae6b4',   // Light green
    nurse: '#fbd38d',     // Light orange
    office: '#e9d8fd',    // Light purple
    hallway: '#e2e8f0'    // Light gray
  };
  return colors[type];
};

function formatMetricName(name: string): string {
  return name.split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

function formatMetricValue(value: number, metricName: string): string {
  // Infer the type of metric from its name and value
  const name = metricName.toLowerCase();
  
  // Time-based metrics typically have "time", "hours", or "hrs" in the name
  if (name.includes('time') || name.includes('hours') || name.includes('hrs')) {
    return `${value.toFixed(1)} hrs`;
  }
  
  // Count-based metrics typically have "count", "number", or "assigned" in the name
  // or are whole numbers less than 100
  if (name.includes('count') || name.includes('number') || name.includes('assigned') || 
      (value < 100 && Number.isInteger(value))) {
    return value.toFixed(0);
  }
  
  // Risk-based metrics have "risk" in the name
  if (name.includes('risk')) {
    return `Level ${value.toFixed(0)}`;
  }
  
  // Score-based metrics have "score" in the name
  if (name.includes('score')) {
    return value.toFixed(1);
  }
  
  // Rate-based metrics have "rate" in the name
  if (name.includes('rate')) {
    return value.toFixed(1) + '%';
  }
  
  // For metrics ending in "pct" or "percent" or have "completion" in the name
  if (name.endsWith('pct') || name.includes('percent') || name.includes('completion')) {
    return value.toFixed(1) + '%';
  }
  
  // Default format: if value is between 0-100, treat as percentage, otherwise show fixed decimal
  return (value >= 0 && value <= 100) ? value.toFixed(1) + '%' : value.toFixed(1);
};

function getFormattedRoomType(type: string): string {
  return type.split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

interface FloorLayoutProps {
  floorName: string;
  rooms: Room[];
  selectedMetric?: string;
  metrics: Array<{
    floor: string;
    room?: string;
    metric_name: string;
    value: number;
  }>;
  onRoomSelect?: (room: Room) => void;
}

export function FloorLayout({
  floorName,
  rooms,
  selectedMetric,
  metrics,
  onRoomSelect
}: FloorLayoutProps) {
  const [hoveredRoom, setHoveredRoom] = useState<string | null>(null);
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  const [showDetailView, setShowDetailView] = useState(false);

  const colorScale = useMemo(() => {
    if (!selectedMetric) return null;
    const values = metrics
      .filter(m => m.metric_name === selectedMetric)
      .map(m => m.value);
    return getColorScale(values);
  }, [metrics, selectedMetric]);

  const getRoomColor = (room: Room) => {
    if (!selectedMetric || !colorScale) return null;
    const metric = metrics.find(
      m => m.room === room.id && m.metric_name === selectedMetric
    );
    return metric ? colorScale(metric.value) : null;
  };

  const getRoomMetrics = (roomId: string) => {
    return metrics.filter(m => m.room === roomId);
  };

  const handleRoomClick = (room: Room) => {
    if (room.type !== 'hallway') {
      setSelectedRoom(room.id);
      setShowDetailView(true);
    }
    onRoomSelect?.(room);
  };

  return (
    <group>
      <mesh
        receiveShadow
        position={[0, -0.1, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
      >
        <planeGeometry args={[100, 60]} />
        <meshStandardMaterial
          color="#f0f0f0"
          roughness={0.8}
          metalness={0.2}
        />
      </mesh>

      {showDetailView && selectedRoom ? (
        <RoomDetail
          room={rooms.find(r => r.id === selectedRoom)!}
          onClose={() => {
            setShowDetailView(false);
            setSelectedRoom(null);
          }}
        />
      ) : (
        <group>
          {rooms.map((room) => (
            <RoomMesh
              key={room.id}
              room={room}
              isSelected={selectedRoom === room.id}
              isHovered={hoveredRoom === room.id}
              onClick={() => handleRoomClick(room)}
              onPointerOver={() => setHoveredRoom(room.id)}
              onPointerOut={() => setHoveredRoom(null)}
              metricColor={getRoomColor(room)}
              metrics={getRoomMetrics(room.id)}
            />
          ))}
        </group>
      )}

      <Billboard>
        <Text
          position={[0, 8, -25]}
          fontSize={2}
          color="black"
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.04}
          outlineColor="#ffffff"
        >
          {floorName}
        </Text>
      </Billboard>
    </group>
  );
};

export default FloorLayout;