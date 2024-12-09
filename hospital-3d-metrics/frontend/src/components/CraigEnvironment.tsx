import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { useThree } from '@react-three/fiber';

interface SimplifiedBuilding {
  position: [number, number, number];
  size: [number, number, number];
  color: string;
}

export const CraigEnvironment = () => {
  const { scene } = useThree();
  const treesRef = useRef<THREE.InstancedMesh>(null);

  // Materials
  const pavementMaterial = new THREE.MeshStandardMaterial({
    color: '#2c2c2c',
    roughness: 0.8,
    metalness: 0.1
  });

  const grassMaterial = new THREE.MeshStandardMaterial({
    color: '#2d5a27',
    roughness: 0.9,
    metalness: 0.1
  });

  const roadMaterial = new THREE.MeshStandardMaterial({
    color: '#1a1a1a',
    roughness: 0.7,
    metalness: 0.2
  });

  // Surrounding buildings data
  const surroundingBuildings: SimplifiedBuilding[] = [
    // Medical offices west of Craig
    { position: [-40, 0, 0], size: [20, 15, 30], color: '#d4d4d4' },
    // Buildings east of Craig
    { position: [40, 0, 0], size: [25, 12, 35], color: '#e0e0e0' },
    // Residential buildings
    { position: [0, 0, -60], size: [120, 8, 20], color: '#c0c0c0' },
    { position: [0, 0, 60], size: [120, 8, 20], color: '#c0c0c0' },
  ];

  useEffect(() => {
    if (treesRef.current) {
      // Position trees
      const matrix = new THREE.Matrix4();
      for (let i = 0; i < 50; i++) {
        const position = new THREE.Vector3(
          (Math.random() - 0.5) * 200,
          4,
          (Math.random() - 0.5) * 200
        );
        const scale = new THREE.Vector3(1, 1, 1).multiplyScalar(0.5 + Math.random() * 0.5);
        matrix.compose(position, new THREE.Quaternion(), scale);
        treesRef.current.setMatrixAt(i, matrix);
      }
      treesRef.current.instanceMatrix.needsUpdate = true;
    }
  }, []);

  return (
    <group>
      {/* Base ground plane */}
      <mesh rotation-x={-Math.PI / 2} receiveShadow position={[0, -0.1, 0]}>
        <planeGeometry args={[300, 300]} />
        <meshStandardMaterial color="#a0a0a0" />
      </mesh>

      {/* Main roads */}
      <mesh position={[0, 0, 0]} rotation-x={-Math.PI / 2} receiveShadow>
        <planeGeometry args={[200, 15]} />
        <primitive object={roadMaterial} attach="material" />
      </mesh>

      {/* North-South roads */}
      {[-60, -30, 0, 30, 60].map((x) => (
        <mesh key={x} position={[x, 0, 0]} rotation-x={-Math.PI / 2} receiveShadow>
          <planeGeometry args={[8, 200]} />
          <primitive object={roadMaterial} attach="material" />
        </mesh>
      ))}

      {/* Parking lots */}
      <mesh position={[-20, 0.1, 20]} rotation-x={-Math.PI / 2} receiveShadow>
        <planeGeometry args={[40, 30]} />
        <primitive object={pavementMaterial} attach="material" />
      </mesh>
      <mesh position={[20, 0.1, -20]} rotation-x={-Math.PI / 2} receiveShadow>
        <planeGeometry args={[35, 25]} />
        <primitive object={pavementMaterial} attach="material" />
      </mesh>

      {/* Green spaces */}
      {[[-30, 30], [30, 30], [-30, -30], [30, -30]].map(([x, z], i) => (
        <mesh key={i} position={[x, 0.1, z]} rotation-x={-Math.PI / 2} receiveShadow>
          <planeGeometry args={[20, 20]} />
          <primitive object={grassMaterial} attach="material" />
        </mesh>
      ))}

      {/* Surrounding buildings */}
      {surroundingBuildings.map((building, index) => (
        <mesh
          key={index}
          position={new THREE.Vector3(...building.position)}
          castShadow
          receiveShadow
        >
          <boxGeometry args={building.size} />
          <meshStandardMaterial color={building.color} />
        </mesh>
      ))}

      {/* Trees */}
      <instancedMesh
        ref={treesRef}
        args={[undefined, undefined, 50]}
        castShadow
        receiveShadow
      >
        <sphereGeometry args={[2, 8, 8]} />
        <meshStandardMaterial color="#1a472a" />
      </instancedMesh>
    </group>
  );
};