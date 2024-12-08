// frontend/src/components/HospitalView.tsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { Building } from './Building';
import { Bridge } from './Bridge';
import { Garden } from './Garden';
import { Controls } from './Controls';
import { MetricsPanel } from './MetricsPanel';
import { FloorDetail } from './FloorDetail';
import { useState, useEffect } from 'react';
import * as THREE from 'three';
import { useMetrics } from '../hooks/useMetrics';

// Define building dimensions and positions
const FLOOR_HEIGHT = 3;
const BUILDING_SPACING = 30;
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

// Craig Hospital blue color
const CRAIG_BLUE = '#007dc3';

export const HospitalView = () => {
  // State management
  const [hoveredFloor, setHoveredFloor] = useState<string | null>(null);
  const [selectedFloor, setSelectedFloor] = useState<string | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>('patient_satisfaction');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['Patient Metrics', 'Staff Metrics']);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['patient_satisfaction', 'fall_risk', 'staff_retention']);
  const [showFloorDetail, setShowFloorDetail] = useState(false);

  // Fetch metrics using the custom hook
  const { metrics, loading, error, fetchMetrics } = useMetrics();

  useEffect(() => {
    fetchMetrics();
  }, []);

  // Handle metric selection change
  const handleMetricChange = (metric: string) => {
    setSelectedMetric(metric);
  };

  // Handle category selection change
  const handleCategoryChange = (categories: string[]) => {
    setSelectedCategories(categories);
  };

  // Handle metrics selection change
  const handleMetricsSelectionChange = (metrics: string[]) => {
    setSelectedMetrics(metrics);
  };

  // Handle floor click for floor detail view
  const handleFloorClick = (floor: string) => {
    if (selectedFloor === floor) {
      setSelectedFloor(null);
      setShowFloorDetail(false);
    } else {
      setSelectedFloor(floor);
      setShowFloorDetail(true);
    }
  };

  return (
    <div className="w-screen h-screen">
      <Controls
        onMetricChange={handleMetricChange}
        onCategoryChange={handleCategoryChange}
        onMetricsSelectionChange={handleMetricsSelectionChange}
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
      />

      <Canvas shadows>
        <PerspectiveCamera makeDefault position={[75, 45, 0]} />
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          minDistance={30}
          maxDistance={150}
          maxPolarAngle={Math.PI / 2}
        />

        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[20, 20, 0]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />

        {/* Ground */}
        <mesh
          rotation-x={-Math.PI / 2}
          receiveShadow
          position={[0, -0.1, 0]}
        >
          <planeGeometry args={[100, 100]} />
          <meshStandardMaterial color="#a0a0a0" />
        </mesh>

{/* Buildings */}
        {!showFloorDetail && Object.entries(buildingConfigs).map(([name, config]) => (
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

        {showFloorDetail && selectedFloor && (
          <FloorDetail
            floorData={getFloorData(selectedFloor)}
            onClose={() => {
              setSelectedFloor(null);
              setShowFloorDetail(false);
            }}
          />
        )}

        {/* Bridges */}
        {!showFloorDetail && (
          <>
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
          </>
        )}

        {/* Garden */}
        {!showFloorDetail && (
          <Garden
            position={[15, 0, BUILDING_SPACING/2]}
            width={8}
            depth={12}
          />
        )}
      </Canvas>
    </div>
  );
};