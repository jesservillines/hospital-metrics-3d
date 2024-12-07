import { useEffect, useMemo } from 'react'
import * as THREE from 'three'
import { Vector3, Euler } from 'three'
import { getColorScale } from '../utils/colorScales'

interface BuildingProps {
  name: string
  position: Vector3
  width: number
  height: number
  depth: number
  floorCount: number
  floorHeight: number
  onHoverFloor: (floor: string | null) => void
  onSelectFloor: (floor: string | null) => void
  hoveredFloor: string | null
  selectedFloor: string | null
  selectedColor: string
  metricData?: { [key: string]: number }  // New prop for metric data
  currentMetric?: string                   // New prop for current metric
  rotation?: [number, number, number]
}

export const Building = ({
  name,
  position,
  width,
  height,
  depth,
  floorCount,
  floorHeight,
  onHoverFloor,
  onSelectFloor,
  hoveredFloor,
  selectedFloor,
  selectedColor,
  metricData = {},
  currentMetric,
  rotation = [0, 0, 0]
}: BuildingProps) => {
  // Generate floors with heat map colors
  const floors = useMemo(() => {
    const floorGeometry = new THREE.BoxGeometry(width, floorHeight, depth)
    const floors = []

    // Create color scale if we have metric data
    const values = Object.values(metricData)
    const colorScale = values.length > 0 ? getColorScale(values) : null

    for (let i = 0; i < floorCount; i++) {
      const floorName = `${i + 1} ${name}`
      const isHovered = hoveredFloor === floorName
      const isSelected = selectedFloor === floorName
      const floorY = (i * floorHeight) + (floorHeight / 2)

      // Determine floor color based on metric data or default to white
      let floorColor = '#ffffff'
      if (currentMetric && metricData[floorName]) {
        floorColor = colorScale ? colorScale(metricData[floorName]) : '#ffffff'
      }

      floors.push(
        <mesh
          key={floorName}
          position={[0, floorY, 0]}
          geometry={floorGeometry}
          onPointerOver={(e) => {
            e.stopPropagation()
            onHoverFloor(floorName)
          }}
          onPointerOut={() => onHoverFloor(null)}
          onClick={(e) => {
            e.stopPropagation()
            onSelectFloor(isSelected ? null : floorName)
          }}
        >
          <meshStandardMaterial
            color={isSelected ? selectedColor : isHovered ? '#e0e0e0' : floorColor}
            transparent
            opacity={0.8}
          />
        </mesh>
      )
    }
    return floors
  }, [name, width, height, depth, floorCount, floorHeight, hoveredFloor, selectedFloor, selectedColor, metricData, currentMetric])

  return (
    <group position={position} rotation={new THREE.Euler(...rotation)}>
      {floors}
    </group>
  )
}