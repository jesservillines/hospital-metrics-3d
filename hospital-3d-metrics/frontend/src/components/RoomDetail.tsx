import { useEffect, useRef } from 'react';
import { Text, Billboard, Html } from '@react-three/drei';
import * as THREE from 'three';

interface RoomMetrics {
  occupancy?: number;
  nurseResponseTime?: number;
  patientSatisfaction?: number;
  equipmentUtilization?: number;
  lastCleaned?: Date;
  temperatureF?: number;
  humidityPercent?: number;
  co2Level?: number;
  staffUtilization?: number;
  documentationCompletion?: number;
  patientsAssigned?: number;
}

interface RoomProperties {
  maxOccupancy: number;
  hasOxygen?: boolean;
  hasTelemetry?: boolean;
  isNegativePressure?: boolean;
  isIsolation?: boolean;
  equipmentList?: string[];
  specialFeatures?: string[];
  squareFootage: number;
  windowCount: number;
}

interface Room {
  id: string;
  name: string;
  type: 'patient' | 'nurse' | 'storage' | 'treatment' | 'hallway';
  metrics: RoomMetrics;
  properties: RoomProperties;
}

interface RoomDetailProps {
  room: Room;
  onClose: () => void;
}

function getMetricDisplays(room: Room) {
  switch (room.type) {
    case 'patient':
      return [
        { label: 'Occupancy', value: `${room.metrics?.occupancy}%` },
        { label: 'Temperature', value: `${room.metrics?.temperatureF}°F` },
        { label: 'Humidity', value: `${room.metrics?.humidityPercent}%` },
        { label: 'Nurse Response Time', value: `${room.metrics?.nurseResponseTime} min` },
      ];
    case 'nurse':
      return [
        { label: 'Staff Utilization', value: `${room.metrics?.staffUtilization}%` },
        { label: 'Patients Assigned', value: room.metrics?.patientsAssigned },
        { label: 'Documentation', value: `${room.metrics?.documentationCompletion}%` },
      ];
    case 'storage':
      return [
        { label: 'Equipment Utilization', value: `${room.metrics?.equipmentUtilization}%` },
        { label: 'Storage Capacity', value: `${room.metrics?.occupancy}%` },
      ];
    case 'treatment':
      return [
        { label: 'Patient Satisfaction', value: `${room.metrics?.patientSatisfaction}%` },
        { label: 'Treatment Capacity', value: `${room.metrics?.occupancy}%` },
      ];
    case 'hallway':
      return [];
    default:
      return [];
  }
};

function getPropertyDisplays(room: Room) {
  const properties = room.properties || {};
  const displays = [
    { label: 'Square Footage', value: properties.squareFootage },
    { label: 'Max Occupancy', value: properties.maxOccupancy },
  ];

  if (room.type === 'patient') {
    displays.push(
      { label: 'Oxygen Available', value: properties.hasOxygen ? 'Yes' : 'No' },
      { label: 'Telemetry', value: properties.hasTelemetry ? 'Yes' : 'No' },
      { label: 'Negative Pressure', value: properties.isNegativePressure ? 'Yes' : 'No' }
    );
  }

  return displays;
};

export function RoomDetail({ room, onClose }: RoomDetailProps) {
  const roomRef = useRef<THREE.Group>(null);
  const height = room.type === 'hallway' ? 0.5 : 3;

  useEffect(() => {
    if (roomRef.current) {
      roomRef.current.rotation.x = 0;
      roomRef.current.position.set(0, 0, 0);
    }
  }, [room]);

  return (
    <group ref={roomRef}>
      {/* Room base */}
      <mesh position={[0, 0, 0]} castShadow receiveShadow>
        <boxGeometry args={[room.width * 2, height, room.depth * 2]} />
        <meshStandardMaterial color="#f0f8ff" transparent opacity={0.8} />
      </mesh>

      {/* Room features */}
      <group>
        {room.type === 'patient' && (
          <>
            <mesh position={[-2, 0.3, 0]} castShadow>
              <boxGeometry args={[2.5, 0.6, 1.8]} />
              <meshStandardMaterial color="#ffffff" />
            </mesh>
            <mesh position={[room.width - 0.5, 1.5, 0]} castShadow>
              <boxGeometry args={[0.2, 2, 2]} />
              <meshStandardMaterial color="#87ceeb" transparent opacity={0.4} />
            </mesh>
          </>
        )}
      </group>

      {/* Room information panel */}
      <Html position={[0, 4, 0]} center>
        <div className="bg-white p-6 rounded-lg shadow-lg min-w-[300px]">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">{room.name}</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              Close
            </button>
          </div>

          <div className="space-y-4">
            <div className="bg-gray-50 p-3 rounded">
              <h3 className="font-semibold mb-2">Room Properties</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                {getPropertyDisplays(room).map((prop, index) => (
                  <React.Fragment key={index}>
                    <span className="text-gray-600">{prop.label}:</span>
                    <span className="font-medium">{prop.value}</span>
                  </React.Fragment>
                ))}
              </div>
            </div>

            {room.metrics && (
              <div className="bg-blue-50 p-3 rounded">
                <h3 className="font-semibold mb-2">Current Metrics</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {getMetricDisplays(room).map((metric, index) => (
                    <React.Fragment key={index}>
                      <span className="text-gray-600">{metric.label}:</span>
                      <span className="font-medium">{metric.value}</span>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </Html>

      {/* Room label */}
      <Billboard>
        <Text
          position={[0, height + 1.5, 0]}
          fontSize={0.8}
          color="black"
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.05}
          outlineColor="white"
        >
          {room.name}
        </Text>
      </Billboard>
    </group>
  );
};

export default RoomDetail;