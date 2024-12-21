import { useRef } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'

interface GardenProps {
  position: THREE.Vector3 | [number, number, number]
  width: number
  depth: number
}

export function Garden({ position, width, depth }: GardenProps) {
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
        receiveShadow
      >
        <planeGeometry args={[width, depth]} />
        <meshStandardMaterial
          color="#228B22"
          transparent
          opacity={0.8}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Decorative elements */}
      <mesh position={[width/4, 0.5, depth/4]}>
        <sphereGeometry args={[0.5]} />
        <meshStandardMaterial color="#006400" />
      </mesh>

      <mesh position={[-width/4, 0.3, -depth/4]}>
        <sphereGeometry args={[0.3]} />
        <meshStandardMaterial color="#228B22" />
      </mesh>
    </group>
  )
}

export default Garden;