// frontend/src/components/HospitalView.tsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import Building from './Building';
import Bridge from './Bridge';
import Garden from './Garden';
import Controls from './Controls';
import MetricsPanel from './MetricsPanel';
import FloorDetail from './FloorDetail';
import { SettingsWidget } from './SettingsWidget';
import { useMetrics } from '../hooks/useMetrics';
import { roomDataService } from '../services/roomDataService';
import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import * as THREE from 'three';

// Constants
const FLOOR_HEIGHT = 3;
const BUILDING_SPACING = 30;
const EXPLOSION_HEIGHT = FLOOR_HEIGHT * 5;
const DEFAULT_COLOR = '#007dc3';

// Static configurations
const FLOOR_LEVEL_METRICS = {
  metrics: [
    { value: 'patient_satisfaction', label: 'Patient Satisfaction', category: 'Patient Metrics' },
    { value: 'staff_retention', label: 'Staff Retention', category: 'Staff Metrics' },
    { value: 'fall_risk_average', label: 'Fall Risk Average', category: 'Patient Metrics' },
    { value: 'nurse_response_time_avg', label: 'Nurse Response Time', category: 'Staff Metrics' },
    { value: 'therapy_completion_rate', label: 'Therapy Completion', category: 'Patient Metrics' },
    { value: 'equipment_utilization', label: 'Equipment Utilization', category: 'Room Metrics' },
    { value: 'department_efficiency', label: 'Department Efficiency', category: 'Staff Metrics' },
    { value: 'space_utilization', label: 'Space Utilization', category: 'Room Metrics' }
  ],
  categories: ['Patient Metrics', 'Staff Metrics', 'Room Metrics']
};

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

export function HospitalView() {
  // State
  const [hoveredFloor, setHoveredFloor] = useState<string | null>(null);
  const [selectedFloor, setSelectedFloor] = useState<string | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>('patient_satisfaction');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(FLOOR_LEVEL_METRICS.categories.slice(0, 2));
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(FLOOR_LEVEL_METRICS.metrics.filter(m => ['Patient Metrics', 'Staff Metrics'].includes(m.category)).map(m => m.value));
  const [showFloorDetail, setShowFloorDetail] = useState(false);
  const [isDataLoaded, setIsDataLoaded] = useState(false);
  const [heatmapColor, setHeatmapColor] = useState(DEFAULT_COLOR);

  // Refs
  const controlsRef = useRef<any>(null);
  const initialPosition = useMemo(() => new THREE.Vector3(75, 45, 0), []);

  // Hooks
  const {
    metrics,
    loading,
    error,
    fetchFloorMetrics,
    fetchHeatmapData,
    currentMetrics,
    fetchAllFloorMetrics,
    fetchMetricsForFloor
  } = useMetrics();

  // Initialize room data
  useEffect(() => {
    const initData = async () => {
      try {
        await roomDataService.loadFromCSV('/data/floor_layout.csv');
        await fetchAllFloorMetrics();
        setIsDataLoaded(true);
        console.log('Room data loaded successfully');
      } catch (error) {
        console.error('Error loading data:', error);
      }
    };

    initData();
  }, [fetchAllFloorMetrics]);

  // Handle floor selection
  const handleFloorClick = useCallback(async (floor: string | null) => {
    console.log('Floor clicked:', floor);

    if (floor === selectedFloor && showFloorDetail) {
      setSelectedFloor(null);
      setShowFloorDetail(false);
      return;
    }

    if (floor) {
      const [floorNumber, wing] = floor.split(' ');
      const floorId = `${floorNumber}_${wing.toLowerCase()}`;
      console.log('Fetching metrics for floor:', floorId);
      
      try {
        await fetchMetricsForFloor(floorId);
        setSelectedFloor(floor);
        setShowFloorDetail(true);
      } catch (error) {
        console.error('Error fetching floor metrics:', error);
      }
    } else {
      setSelectedFloor(null);
      setShowFloorDetail(false);
    }
  }, [fetchMetricsForFloor, selectedFloor, showFloorDetail]);

  const handleMetricChange = useCallback(async (metric: string) => {
    setSelectedMetric(metric);
    if (selectedFloor) {
      await fetchHeatmapData(selectedFloor, metric);
    }
  }, [selectedFloor, fetchHeatmapData]);

  const getFilteredMetrics = useCallback((metrics: any[]) => {
    // Get the mapping of metric names to categories
    const metricCategories = Object.fromEntries(
      FLOOR_LEVEL_METRICS.metrics.map(m => [m.value, m.category])
    );

    return metrics.filter(metric => {
      const category = metricCategories[metric.metric_name];
      return (
        metric.metric_type === 'floor' &&
        selectedMetrics.includes(metric.metric_name) &&
        selectedCategories.includes(category)
      );
    });
  }, [selectedMetrics, selectedCategories]);

  if (loading || !isDataLoaded) {
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <div className="text-lg">Loading hospital data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-screen h-screen flex items-center justify-center">
        <div className="text-lg text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="w-screen h-screen">
      <Controls
        onMetricChange={handleMetricChange}
        onCategoryChange={setSelectedCategories}
        onMetricsSelectionChange={setSelectedMetrics}
        selectedMetric={selectedMetric}
        selectedCategories={selectedCategories}
        selectedMetrics={selectedMetrics}
        showFloorDetail={showFloorDetail}
        availableMetrics={FLOOR_LEVEL_METRICS}
      />

      <SettingsWidget
        onColorChange={setHeatmapColor}
        currentColor={heatmapColor}
      />

      {(hoveredFloor || selectedFloor) && (
        <MetricsPanel
          hoveredFloor={hoveredFloor}
          selectedFloor={selectedFloor}
          metrics={getFilteredMetrics(currentMetrics)}
          selectedCategories={selectedCategories}
          selectedMetrics={selectedMetrics}
          showFloorDetail={showFloorDetail}
          onClose={() => {
            setSelectedFloor(null);
            setShowFloorDetail(false);
          }}
        />
      )}

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
          position={[50, 50, 25]}
          intensity={0.8}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          shadow-camera-far={100}
          shadow-camera-left={-50}
          shadow-camera-right={50}
          shadow-camera-top={50}
          shadow-camera-bottom={-50}
        />

        <mesh
          rotation-x={-Math.PI / 2}
          position={[0, -0.1, 0]}
          receiveShadow
        >
          <planeGeometry args={[1000, 1000]} />
          <meshStandardMaterial color="#a0a0a0" />
        </mesh>

        {/* Hospital Buildings */}
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
              selectedColor={heatmapColor}
              metrics={currentMetrics}
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
        </group>

        {/* Floor Detail View */}
        {showFloorDetail && selectedFloor && (
          <group position={[0, EXPLOSION_HEIGHT, 0]}>
            <FloorDetail
              floorName={selectedFloor}
              onClose={() => {
                setSelectedFloor(null);
                setShowFloorDetail(false);
                // Reset camera position
                if (controlsRef.current) {
                  controlsRef.current.target.set(0, 0, 0);
                  controlsRef.current.object.position.copy(initialPosition);
                  controlsRef.current.update();
                }
              }}
              metrics={currentMetrics}
              selectedMetric={selectedMetric}
              roomsData={roomDataService}
              selectedColor={heatmapColor}
            />
          </group>
        )}
      </Canvas>
    </div>
  );
}

export default HospitalView;