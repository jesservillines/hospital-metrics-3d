// frontend/src/components/HospitalView.tsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import Building from './Building';
import Bridge from './Bridge';
import Garden from './Garden';
import Controls from './Controls';
import MetricsPanel from './MetricsPanel';
import FloorDetail from './FloorDetail';
import RoomMetricsPanel from './RoomMetricsPanel';
import { SettingsWidget } from './SettingsWidget';
import DateSlider from './DateSlider';
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

export default function HospitalView() {
  // State
  const [hoveredFloor, setHoveredFloor] = useState<string | null>(null);
  const [selectedFloor, setSelectedFloor] = useState<string | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<string>('patient_satisfaction');
  const [selectedRoomMetric, setSelectedRoomMetric] = useState<string>('fall_risk');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['Patient Metrics']);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['patient_satisfaction']);
  const [showFloorDetail, setShowFloorDetail] = useState(false);
  const [isDataLoaded, setIsDataLoaded] = useState(false);
  const [heatmapColor, setHeatmapColor] = useState(DEFAULT_COLOR);
  const [selectedRoomColor, setSelectedRoomColor] = useState<string>('#ff0000');
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [debug, setDebug] = useState<any>({});

  // Debug log for initial state
  useEffect(() => {
    console.log('Initial state:', {
      selectedMetric,
      selectedCategories,
      selectedMetrics,
      FLOOR_LEVEL_METRICS
    });
  }, [selectedMetric, selectedCategories, selectedMetrics]);

  // Refs
  const controlsRef = useRef<any>(null);
  const initialPosition = useMemo(() => new THREE.Vector3(75, 45, 0), []);

  // Hooks
  const {
    metrics: { floorMetrics, roomMetrics },
    currentMetrics,
    loading,
    error,
    fetchAllFloorMetrics,
    fetchMetricsForFloor
  } = useMetrics();

  // Add debug logging
  useEffect(() => {
    console.log('HospitalView State:', {
      hoveredFloor,
      selectedFloor,
      selectedCategories,
      selectedMetrics,
      selectedDate,
      metricsCount: currentMetrics?.length,
      loading,
      error
    });
  }, [hoveredFloor, selectedFloor, selectedCategories, selectedMetrics, selectedDate, currentMetrics, loading, error]);

  // Handle floor selection
  const handleFloorClick = useCallback(async (floor: string | null) => {
    console.log('Floor clicked:', floor);

    if (floor === selectedFloor && showFloorDetail) {
      console.log('Exiting floor detail mode...');
      setSelectedFloor(null);
      setShowFloorDetail(false);
      
      // Refetch all floor metrics when exiting floor detail mode
      console.log('Refetching all metrics...');
      try {
        await fetchAllFloorMetrics();
        console.log('Successfully refetched all metrics');
      } catch (error) {
        console.error('Error refetching metrics:', error);
      }
      return;
    }

    if (floor) {
      try {
        // The floor name comes as "4 West", convert to "4_west" to match database format
        const [floorNumber, wing] = floor.split(' ');
        const floorId = `${floorNumber}_${wing.toLowerCase()}`;
        console.log('Floor ID for API:', floorId);
        
        // Fetch metrics for the floor
        const roomMetrics = await fetchMetricsForFloor(floorId);
        console.log('Fetched room metrics for floor:', roomMetrics);
        
        if (roomMetrics.length === 0) {
          console.warn('No room metrics found for floor:', floorId);
        }
        
        // Update the selected floor and show detail
        setSelectedFloor(floor);
        setShowFloorDetail(true);
      } catch (error) {
        console.error('Error fetching floor metrics:', error);
      }
    } else {
      console.log('Clearing floor selection...');
      setSelectedFloor(null);
      setShowFloorDetail(false);
      
      // Refetch all floor metrics when clearing floor selection
      console.log('Refetching all metrics...');
      try {
        await fetchAllFloorMetrics();
        console.log('Successfully refetched all metrics');
      } catch (error) {
        console.error('Error refetching metrics:', error);
      }
    }
  }, [fetchMetricsForFloor, selectedFloor, showFloorDetail, fetchAllFloorMetrics]);

  // Effect to monitor metrics state
  useEffect(() => {
    console.log('Current metrics state:', {
      totalMetrics: currentMetrics?.length,
      selectedFloor,
      showFloorDetail,
      sampleMetrics: currentMetrics?.slice(0, 2)
    });
  }, [currentMetrics, selectedFloor, showFloorDetail]);

  // Render floor detail when a floor is selected
  const renderFloorDetail = useCallback(() => {
    if (!selectedFloor || !showFloorDetail) return null;

    return (
      <group position={[0, EXPLOSION_HEIGHT, 0]}>
        <FloorDetail
          floorName={selectedFloor}
          onClose={() => handleFloorClick(null)}
          metrics={roomMetrics}  
          selectedMetric={selectedRoomMetric}
          roomsData={roomDataService}
          selectedColor={selectedRoomColor}
        />
      </group>
    );
  }, [selectedFloor, showFloorDetail, roomMetrics, selectedRoomMetric, selectedRoomColor, handleFloorClick]);

  // Initialize room data
  useEffect(() => {
    const initData = async () => {
      try {
        console.log('Starting to load room data...');
        await roomDataService.loadFromCSV('/data/floor_layout.csv');
        console.log('Room data loaded successfully');
        
        // After room data is loaded, fetch initial metrics
        await fetchAllFloorMetrics();
        setIsDataLoaded(true);
      } catch (error) {
        console.error('Error loading data:', error);
      }
    };

    initData();
  }, [fetchAllFloorMetrics]);

  // Filter metrics by date and other criteria
  const filteredMetrics = useMemo(() => {
    if (!currentMetrics) return [];

    console.log('Filtering metrics:', {
      totalMetrics: currentMetrics.length,
      selectedDate,
      selectedCategories,
      selectedMetrics
    });

    const filtered = currentMetrics.filter(metric => {
      // If no date is selected, show the latest date's metrics
      if (!selectedDate) {
        const dates = currentMetrics.map(m => m.timestamp.split('T')[0]);
        const latestDate = dates.sort().pop();
        return metric.timestamp.startsWith(latestDate!);
      }

      const metricDate = metric.timestamp.split('T')[0];
      const dateMatches = metricDate === selectedDate;
      const categoryMatches = selectedCategories.includes(metric.metric_category);
      const metricMatches = selectedMetrics.includes(metric.metric_name);

      const matches = dateMatches && (categoryMatches || metricMatches);

      // Debug individual metric filtering
      if (debug.metrics) {
        console.log('Metric filtering:', {
          metric: metric.metric_name,
          floor: metric.floor_id,
          date: metricDate,
          dateMatches,
          categoryMatches,
          metricMatches,
          included: matches
        });
      }

      return matches;
    });

    console.log('Filtered metrics result:', {
      filteredCount: filtered.length,
      sampleMetric: filtered[0]
    });

    return filtered;
  }, [currentMetrics, selectedDate, selectedCategories, selectedMetrics, debug.metrics]);

  const handleMetricChange = useCallback(async (metric: string) => {
    setSelectedMetric(metric);
    if (selectedFloor) {
      await fetchMetricsForFloor(selectedFloor);
    }
  }, [selectedFloor, fetchMetricsForFloor]);

  const handleRoomMetricChange = useCallback(async (metric: string) => {
    setSelectedRoomMetric(metric);
    if (selectedFloor) {
      await fetchMetricsForFloor(selectedFloor);
    }
  }, [selectedFloor, fetchMetricsForFloor]);

  // Toggle debug mode with keyboard shortcut
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'd') {
        setDebug(prev => ({
          ...prev,
          metrics: !prev.metrics
        }));
        console.log('Debug mode toggled');
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  // Handle messages from Streamlit
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'config_update') {
        const config = event.data.config;
        console.log('Received config from Streamlit:', config);

        // Update state based on Streamlit configuration
        if (config.startDate) setSelectedDate(config.startDate);
        if (config.metric) setSelectedMetric(config.metric);
        if (config.categories) setSelectedCategories(config.categories);
        if (config.colorScheme) setHeatmapColor(config.colorScheme);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Send updates to Streamlit
  useEffect(() => {
    const sendUpdate = () => {
      if (window.parent) {
        window.parent.postMessage({
          type: 'metrics_update',
          data: {
            selectedFloor,
            selectedMetric,
            selectedCategories,
            metrics: currentMetrics
          }
        }, '*');
      }
    };

    sendUpdate();
  }, [selectedFloor, selectedMetric, selectedCategories, currentMetrics]);

  if (!isDataLoaded) {
    return <div>Loading...</div>;
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

      <RoomMetricsPanel
        selectedMetric={selectedRoomMetric}
        onMetricChange={handleRoomMetricChange}
        metricOptions={[
          { value: 'fall_risk', label: 'Patient Fall Risk' },
          { value: 'patient_satisfaction', label: 'Patient Satisfaction' }
        ]}
        selectedColor={selectedRoomColor}
        onColorChange={setSelectedRoomColor}
        isVisible={showFloorDetail}
      />

      <SettingsWidget
        onColorChange={setHeatmapColor}
        currentColor={heatmapColor}
      />

      {(hoveredFloor || selectedFloor) && (
        <MetricsPanel
          hoveredFloor={hoveredFloor}
          selectedFloor={selectedFloor}
          metrics={filteredMetrics} 
          selectedCategories={selectedCategories}
          selectedMetrics={selectedMetrics}
          showFloorDetail={showFloorDetail}
          onClose={() => {
            setSelectedFloor(null);
            setShowFloorDetail(false);
          }}
        />
      )}

      <DateSlider onDateChange={setSelectedDate} />

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
              metrics={filteredMetrics} 
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
        {renderFloorDetail()}
      </Canvas>
    </div>
  );
}