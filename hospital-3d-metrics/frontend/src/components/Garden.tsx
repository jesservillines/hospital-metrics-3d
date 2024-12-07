import { useRef } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'

interface GardenProps {
  position: THREE.Vector3 | [number, number, number]
  width: number
  depth: number
}

export const Garden = ({ position, width, depth }: GardenProps) => {
  const grassRef = useRef<THREE.Mesh>(null)

  // Create a subtle animation for the grass
  useFrame(({ clock }) => {
    if (grassRef.current) {
      grassRef.current.material.opacity = 0.8 + Math.sin(clock.getElapsedTime()) * 0.1
    }
  })

  return (
    <group position={position}>
      {/* Garden base */}
      <mesh
        rotation-x={-Math.PI / 2}
        receiveShadow
      >
        <planeGeometry args={[width, depth]} />
        <meshStandardMaterial color="#654321" />
      </mesh>

      {/* Grass */}
      <mesh
        ref={grassRef}
        position={[0, 0.1, 0]}
        rotation-x={-Math.PI / 2}
      >
        <planeGeometry args={[width, depth]} />
        <meshStandardMaterial
          color="#228B22"
          transparent
          opacity={0.8}
        />
      </mesh>

      {/* Trees/Bushes */}
      {Array.from({ length: 5 }).map((_, i) => (
        <group
          key={i}
          position={[
            (Math.random() - 0.5) * width * 0.8,
            1,
            (Math.random() - 0.5) * depth * 0.8
          ]}
        >
          {/* Tree trunk */}
          <mesh castShadow>
            <cylinderGeometry args={[0.2, 0.2, 2, 8]} />
            <meshStandardMaterial color="#4A3C2A" />
          </mesh>
          {/* Tree foliage */}
          <mesh position={[0, 1.5, 0]} castShadow>
            <sphereGeometry args={[1, 16, 16]} />
            <meshStandardMaterial color="#006400" />
          </mesh>
        </group>
      ))}
    </group>
  )
}