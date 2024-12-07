import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera } from '@react-three/drei'
import { Building } from './Building'
import { Bridge } from './Bridge'
import { Garden } from './Garden'
import { Controls } from './Controls'
import { MetricsPanel } from './MetricsPanel'
import { useState, useEffect } from 'react'
import { useMetrics } from '../hooks/useMetrics'
import * as THREE from 'three'

// Building configs remain the same...
const FLOOR_HEIGHT = 3
const BUILDING_SPACING = 30
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
}

const CRAIG_BLUE = '#007dc3'

export const HospitalView = () => {
  const [hoveredFloor, setHoveredFloor] = useState<string | null>(null)
  const [selectedFloor, setSelectedFloor] = useState<string | null>(null)
  const [currentMetric, setCurrentMetric] = useState<string>('patient_satisfaction')
  const { metrics, loading, error, fetchMetrics } = useMetrics()

  // Transform metrics data for buildings
  const metricsByFloor = metrics.reduce((acc, metric) => {
    if (metric.metric_name === currentMetric) {
      acc[metric.floor] = metric.value
    }
    return acc
  }, {} as Record<string, number>)

  // Fetch metrics when component mounts or metric changes
  useEffect(() => {
    fetchMetrics(undefined, currentMetric)
  }, [currentMetric])

  // Available metrics for the Controls component
  const availableMetrics = ['patient_satisfaction', 'staff_retention', 'fall_risk']

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      <Canvas shadows>
        {/* Camera and lighting setup remains the same... */}
        <PerspectiveCamera makeDefault position={[50, 30, 0]} />
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          minDistance={20}
          maxDistance={100}
          maxPolarAngle={Math.PI / 2}
        />
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[20, 20, 0]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />

        {/* Ground plane remains the same... */}
        <mesh
          rotation-x={-Math.PI / 2}
          receiveShadow
          position={[0, -0.1, 0]}
        >
          <planeGeometry args={[100, 100]} />
          <meshStandardMaterial color="#a0a0a0" />
        </mesh>

        {/* Buildings with metric data */}
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
            onSelectFloor={setSelectedFloor}
            hoveredFloor={hoveredFloor}
            selectedFloor={selectedFloor}
            selectedColor={CRAIG_BLUE}
            metricData={metricsByFloor}
            currentMetric={currentMetric}
            rotation={[0, Math.PI / 2, 0]}
          />
        ))}

        {/* Bridge and Garden components remain the same... */}
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
      </Canvas>

      {/* UI Controls */}
      <Controls
        onMetricChange={setCurrentMetric}
        onDateRangeChange={() => {}} // To be implemented
        metrics={availableMetrics}
      />

      {/* Metrics Panel */}
      <MetricsPanel
        selectedFloor={selectedFloor}
        metrics={metrics.filter(m => m.floor === selectedFloor)}
      />

      {/* Loading and Error States */}
      {loading && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-white/90 px-4 py-2 rounded-md">
          Loading metrics...
        </div>
      )}
      {error && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-red-100 text-red-700 px-4 py-2 rounded-md">
          Error loading metrics: {error}
        </div>
      )}
    </div>
  )
}