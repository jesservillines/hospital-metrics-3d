import { useState, useCallback, useEffect, useMemo } from 'react';
import * as THREE from 'three';

interface RoomProps {
  position: [number, number, number];
  width: number;
  height: number;
  depth: number;
  roomId: string;
  roomType: string;
  value?: number;
  onRoomSelect: (roomId: string) => void;
  getColorForValue: (value: number) => THREE.Color;
}

export function Room({
  position,
  width,
  height,
  depth,
  roomId,
  roomType,
  value,
  onRoomSelect,
  getColorForValue
}: RoomProps) {
  const [hovered, setHovered] = useState(false);

  // Debug log when room is rendered
  useEffect(() => {
    console.log('Rendering room:', {
      roomId,
      roomType,
      position,
      dimensions: { width, height, depth },
      value
    });
  }, [roomId, roomType, position, width, height, depth, value]);

  const handlePointerOver = useCallback((e: THREE.Event) => {
    e.stopPropagation();
    setHovered(true);
    console.log('Room hovered:', roomId, roomType);
  }, [roomId, roomType]);

  const handlePointerOut = useCallback(() => {
    setHovered(false);
  }, []);

  const handleClick = useCallback((e: THREE.Event) => {
    e.stopPropagation();
    onRoomSelect(roomId);
  }, [onRoomSelect, roomId]);

  // Get the color based on the value
  const color = useMemo(() => {
    if (value === undefined) {
      return new THREE.Color('#e0e0e0'); // Default gray for rooms without data
    }
    return getColorForValue(value);
  }, [value, getColorForValue]);

  return (
    <group>
      <mesh
        position={new THREE.Vector3(...position)}
        onPointerOver={handlePointerOver}
        onPointerOut={handlePointerOut}
        onClick={handleClick}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[width, height, depth]} />
        <meshStandardMaterial
          color={color}
          transparent
          opacity={hovered ? 0.9 : 0.7}
          metalness={0.1}
          roughness={0.8}
          emissive={color}
          emissiveIntensity={0.2}
        />
      </mesh>
      {/* Add a wireframe to help visualize the room boundaries */}
      <lineSegments position={position}>
        <edgesGeometry args={[new THREE.BoxGeometry(width, height, depth)]} />
        <lineBasicMaterial color="#000000" />
      </lineSegments>
    </group>
  );
}

export default Room;
