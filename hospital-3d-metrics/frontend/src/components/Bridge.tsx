import * as THREE from 'three'

interface BridgeProps {
  position: [number, number, number]
  length: number
  width: number
  height: number
  rotation?: [number, number, number]
}

export const Bridge = ({ position, length, width, height, rotation = [0, 0, 1] }: BridgeProps) => {
  return (
    <group position={new THREE.Vector3(...position)} rotation={new THREE.Euler(...rotation)}>
      {/* Main bridge body a0a0ff*/}
      <mesh position={[0, 0, 0]} castShadow receiveShadow>
        <boxGeometry args={[length, height, width]} />
        <meshStandardMaterial color="#a0a0ff" transparent opacity={0.3} />
      </mesh>

              {/* Floor of bridge */}
      <mesh position={[0, -height/2 + 0.1, 0]} castShadow>
        <boxGeometry args={[length, 0.2, width]} />
        <meshStandardMaterial color="#d0d0d0" />
      </mesh>

      {/* Roof of bridge */}
      <mesh position={[0, height/2 - 0.1, 0]} castShadow>
        <boxGeometry args={[length, 0.2, width]} />
        <meshStandardMaterial color="#d0d0d0" />
      </mesh>

      {/* Support structures at ends ffffff*/}
      <mesh position={[0, 0, -width/2]} castShadow>
        <boxGeometry args={[length + 0.1, height, 0.5]} />
        <meshStandardMaterial color="#ffffff" transparent opacity={0.3} />
      </mesh>

      <mesh position={[0, 0, width/2]} castShadow>
        <boxGeometry args={[length + 0.5, height, 0.5]} />
        <meshStandardMaterial color="#d0d0d0" transparent opacity={0.3} />
      </mesh>

      {/* Glass panels */}
      <mesh position={[length/2 - 0.1, 0, 0]} castShadow>
        <boxGeometry args={[0.2, height, width]} />
        <meshStandardMaterial color="#d0d0d0" transparent opacity={0.3} />
      </mesh>

      <mesh position={[-length/2 + 0.1, 0, 0]} castShadow>
        <boxGeometry args={[0.2, height, width]} />
        <meshStandardMaterial color="#d0d0d0" transparent opacity={0.3} />
      </mesh>
    </group>
  )
}