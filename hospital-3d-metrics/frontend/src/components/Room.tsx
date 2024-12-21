import { useState, useCallback } from 'react';
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

  const handlePointerOver = useCallback((e: THREE.Event) => {
    e.stopPropagation();
    setHovered(true);
  }, []);

  const handlePointerOut = useCallback(() => {
    setHovered(false);
  }, []);

  const handleClick = useCallback((e: THREE.Event) => {
    e.stopPropagation();
    onRoomSelect(roomId);
  }, [roomId, onRoomSelect]);

  // Get the color based on the value
  const color = value !== undefined ? getColorForValue(value) : new THREE.Color('#ffffff');

  return (
    <mesh
      position={position}
      onPointerOver={handlePointerOver}
      onPointerOut={handlePointerOut}
      onClick={handleClick}
      castShadow
      receiveShadow
    >
      <boxGeometry args={[width, height, depth]} />
      <meshStandardMaterial
        color={color}
        transparent={true}
        opacity={hovered ? 0.8 : 1}
        metalness={0.1}
        roughness={0.8}
      />
    </mesh>
  );
}

export default Room;
