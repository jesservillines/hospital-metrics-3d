// frontend/src/components/FloorDetail.tsx
import React from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface FloorDetailProps {
  floorData: {
    name: string;
    width: number;
    depth: number;
    height: number;
  };
  onClose: () => void;
}

export const FloorDetail: React.FC<FloorDetailProps> = ({ floorData, onClose }) => {
  // Create a grid of rooms (4x6 grid example)
  const roomsPerRow = 4;
  const roomRows = 6;
  const roomWidth = floorData.width / roomsPerRow;
  const roomDepth = floorData.depth / roomRows;
  const roomHeight = floorData.height * 0.8;
  const spacing = 0.2;

  return (
    <group
      position={[0, 10, 0]} // Lifted position for exploded view
      onClick={(e) => e.stopPropagation()}
    >
      {/* Floor base */}
      <mesh position={[0, 0, 0]} receiveShadow>
        <boxGeometry args={[floorData.width, 0.2, floorData.depth]} />
        <meshStandardMaterial color="#c0c0c0" />
      </mesh>

      {/* Generate rooms */}
      {Array.from({ length: roomRows }).map((_, row) =>
        Array.from({ length: roomsPerRow }).map((_, col) => {
          const x = (col - (roomsPerRow - 1) / 2) * (roomWidth + spacing);
          const z = (row - (roomRows - 1) / 2) * (roomDepth + spacing);

          return (
            <group key={`room-${row}-${col}`} position={[x, roomHeight / 2, z]}>
              {/* Room walls */}
              <mesh castShadow>
                <boxGeometry args={[roomWidth, roomHeight, roomDepth]} />
                <meshStandardMaterial
                  color="#ffffff"
                  transparent
                  opacity={0.8}
                />
              </mesh>
              {/* Room label */}
              <mesh
                position={[0, 0, roomDepth/2 + 0.01]}
                rotation={[0, 0, 0]}
              >
                <planeGeometry args={[roomWidth * 0.8, 0.5]} />
                <meshBasicMaterial color="#000000" />
              </mesh>
            </group>
          );
        })
      )}
    </group>
  );
};