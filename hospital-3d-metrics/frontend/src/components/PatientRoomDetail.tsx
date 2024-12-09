import { useEffect, useRef } from 'react';
import { Text, Billboard, Html } from '@react-three/drei';
import * as THREE from 'three';

interface PatientRoomDetailProps {
  room: {
    id: string;
    name: string;
    type: string;
    width: number;
    depth: number;
    properties?: {
      maxOccupancy?: number;
      hasOxygen?: boolean;
      hasTelemetry?: boolean;
      squareFootage?: number;
    };
    metrics?: {
      occupancy?: number;
      nurseResponseTime?: number;
      patientSatisfaction?: number;
    };
  };
  onClose: () => void;
}

export const PatientRoomDetail = ({ room, onClose }: PatientRoomDetailProps) => {
  const roomRef = useRef<THREE.Group>(null);

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
        <boxGeometry args={[room.width * 2, 3, room.depth * 2]} />
        <meshStandardMaterial color="#f0f8ff" transparent opacity={0.8} />
      </mesh>

      {/* Room features */}
      <group>
        {/* Bed */}
        <mesh position={[-2, 0.3, 0]} castShadow>
          <boxGeometry args={[2.5, 0.6, 1.8]} />
          <meshStandardMaterial color="#ffffff" />
        </mesh>

        {/* Window */}
        <mesh position={[room.width - 0.5, 1.5, 0]} castShadow>
          <boxGeometry args={[0.2, 2, 2]} />
          <meshStandardMaterial color="#87ceeb" transparent opacity={0.4} />
        </mesh>

        {/* Door */}
        <mesh position={[0, 1, room.depth - 0.5]} castShadow>
          <boxGeometry args={[1.2, 2, 0.2]} />
          <meshStandardMaterial color="#8b4513" />
        </mesh>
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
              <h3 className="font-semibold mb-2">Room Details</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span>Square Footage:</span>
                <span>{room.properties?.squareFootage} sq ft</span>
                <span>Max Occupancy:</span>
                <span>{room.properties?.maxOccupancy}</span>
                <span>Oxygen Available:</span>
                <span>{room.properties?.hasOxygen ? 'Yes' : 'No'}</span>
                <span>Telemetry:</span>
                <span>{room.properties?.hasTelemetry ? 'Yes' : 'No'}</span>
              </div>
            </div>

            {room.metrics && (
              <div className="bg-blue-50 p-3 rounded">
                <h3 className="font-semibold mb-2">Current Metrics</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <span>Occupancy:</span>
                  <span>{room.metrics.occupancy}%</span>
                  <span>Response Time:</span>
                  <span>{room.metrics.nurseResponseTime} min</span>
                  <span>Patient Satisfaction:</span>
                  <span>{room.metrics.patientSatisfaction}%</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </Html>

      {/* Room label */}
      <Billboard>
        <Text
          position={[0, 5, 0]}
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