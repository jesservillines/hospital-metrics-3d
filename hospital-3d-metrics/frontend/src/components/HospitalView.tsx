// frontend/src/components/HospitalView.tsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { Building } from './Building';
import { Bridge } from './Bridge';
import { Garden } from './Garden';
import { Controls } from './Controls';
import { MetricsPanel } from './MetricsPanel';
import { FloorDetail } from './FloorDetail';
import { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import { useMetrics } from '../hooks/useMetrics';

const FLOOR_HEIGHT = 3;
const BUILDING_SPACING = 30;
const EXPLOSION_HEIGHT = FLOOR_HEIGHT * 5;
const CRAIG_BLUE = '#007dc3';

const buildingConfigs = {
  West: {
    floors: 4,
    width: 15,
    depth: 35,
    position: new THREE.Vector3(0, 0, -BUILDING_SPACING/2)
  },
  East: {
    floors: 3,
    width: 12.5,
    depth: 25,
    position: new THREE.Vector3(-5, 0, BUILDING_SPACING/2)
  }
};

export const HospitalView = () => {
  const [hoveredFloor, setHoveredFloor] = useState<string | null>(null);
  const [selectedFloor, setSelectedFloor] = useState<string | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>('patient_satisfaction');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['Patient Metrics', 'Staff Metrics']);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['patient_satisfaction', 'fall_risk', 'staff_retention']);
  const [showFloorDetail, setShowFloorDetail] = useState(false);
  const controlsRef = useRef<any>(null);
  const [initialPosition] = useState(() => new THREE.Vector3(75, 45, 0));

  const { metrics, loading, error, fetchMetrics } = useMetrics();

  useEffect(() => {
    fetchMetrics();
  }, []);

  useEffect(() => {
    if (showFloorDetail && controlsRef.current) {
      // Store current camera position before changing to top-down view
      const currentPosition = controlsRef.current.object.position.clone();

      // Only set initial top-down view if it's the first time showing floor detail
      if (!selectedFloor) {
        controlsRef.current.object.position.set(0, EXPLOSION_HEIGHT + 40, 0);
        controlsRef.current.setAzimuthalAngle(0);
        controlsRef.current.setPolarAngle(0);
      } else {
        // Restore previous camera position
        controlsRef.current.object.position.copy(currentPosition);
      }
    }
  }, [showFloorDetail]);

  const handleFloorClick = (floor: string | null) => {
    // If we're already in floor detail mode, ignore clicks on the hospital
    if (showFloorDetail && floor === selectedFloor) {
      return;
    }

    // Normal floor selection handling
    if (selectedFloor === floor) {
      setSelectedFloor(null);
      setShowFloorDetail(false);
    } else {
      setSelectedFloor(floor);
      setShowFloorDetail(!!floor);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="w-screen h-screen">
      <Controls
        onMetricChange={setSelectedMetric}
        onCategoryChange={setSelectedCategories}
        onMetricsSelectionChange={setSelectedMetrics}
        selectedMetric={selectedMetric}
        selectedCategories={selectedCategories}
        selectedMetrics={selectedMetrics}
      />

      <MetricsPanel
        hoveredFloor={hoveredFloor}
        selectedFloor={selectedFloor}
        metrics={metrics || []}
        selectedCategories={selectedCategories}
        selectedMetrics={selectedMetrics}
        showFloorDetail={showFloorDetail}
        onClose={() => {
          setSelectedFloor(null);
          setShowFloorDetail(false);
        }}
      />

      <Canvas shadows>
        <PerspectiveCamera
          makeDefault
          position={initialPosition}
          fov={60}
        />

        <OrbitControls
          ref={controlsRef}
          enableDamping
          dampingFactor={0.05}
          minDistance={30}
          maxDistance={150}
          maxPolarAngle={Math.PI / 2}
        />

        <ambientLight intensity={0.5} />
        <directionalLight
          position={[20, 20, 0]}
          intensity={1}
          castShadow
        />

        <mesh
          rotation-x={-Math.PI / 2}
          receiveShadow
          position={[0, -0.1, 0]}
        >
          <planeGeometry args={[100, 100]} />
          <meshStandardMaterial color="#a0a0a0" />
        </mesh>

        <group scale={showFloorDetail ? 0.3 : 1}>
          {Object.entries(buildingConfigs).map(([name, config]) => (
            <Building
              key={name}
              name={name}
              position={config.position}
              width={config.width}
              height={FLOOR_HEIGHT * config.floors}
              depth={config.depth}
              floorCount={config.floors}
              floorHeight={FLOOR_HEIGHT}
              onHoverFloor={setHoveredFloor}
              onSelectFloor={handleFloorClick}
              hoveredFloor={hoveredFloor}
              selectedFloor={selectedFloor}
              selectedColor={CRAIG_BLUE}
              metrics={metrics || []}
              selectedMetric={selectedMetric}
              rotation={[0, Math.PI / 2, 0]}
            />
          ))}

          <Bridge
            position={[-10, FLOOR_HEIGHT * 1.5, 1]}
            length={4}
            width={BUILDING_SPACING/1.75}
            height={FLOOR_HEIGHT-5.5}
            rotation={[0, 0, 0]}
          />
          <Bridge
            position={[-10, FLOOR_HEIGHT * 2.5, 1]}
            length={4}
            width={BUILDING_SPACING/1.75}
            height={FLOOR_HEIGHT-5.5}
            rotation={[0, 0, 0]}
          />

          <Garden
            position={[15, 0, BUILDING_SPACING/2]}
            width={8}
            depth={12}
          />
        </group>

        {showFloorDetail && selectedFloor && (
          <group position={[0, EXPLOSION_HEIGHT, 0]}>
            <FloorDetail
              floorName={selectedFloor}
              onClose={() => {
                setSelectedFloor(null);
                setShowFloorDetail(false);
              }}
              metrics={metrics || []}
              selectedMetric={selectedMetric}
            />
          </group>
        )}
      </Canvas>
    </div>
  );
};