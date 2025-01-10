import { useMemo } from 'react';
import { Room } from './Room';
import * as THREE from 'three';
import type { Room as RoomType, FloorData } from '../services/roomDataService';

interface RoomData {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface FloorDetailProps {
  floorName: string;
  onClose: () => void;
  metrics: Array<{
    floor_id: string;
    room_id?: string;
    metric_name: string;
    value: number;
    timestamp: string;
    metric_type: 'floor' | 'room';
    metric_category: string;
  }>;
  selectedMetric: string;
  roomsData: any;
  selectedColor: string;
}

export function FloorDetail({
  floorName,
  onClose,
  metrics = [],
  selectedMetric,
  roomsData,
  selectedColor
}: FloorDetailProps) {
  // Get floor data using the service's getFloor method
  const floorRooms = useMemo(() => {
    if (!roomsData?.getFloor) {
      console.error('roomsData or getFloor method is undefined');
      return [];
    }

    try {
      // The floor name comes as "4 West", we need to use it as is for the CSV data
      console.log('Getting floor data for:', floorName);
      const floorData = roomsData.getFloor(floorName) as FloorData | undefined;
      console.log('Raw floor data:', floorData);
      
      if (!floorData?.rooms) {
        console.warn('No rooms found in floor data');
        return [];
      }

      // Log room positions before transformation
      console.log('Room positions before transformation:', 
        floorData.rooms.map(r => ({
          id: r.id,
          x: r.x_position,
          z: r.z_position,
          width: r.width,
          depth: r.depth
        }))
      );

      // Transform room data for rendering
      const transformedRooms = floorData.rooms.map(room => {
        // Scale factors to match the floor plane size
        const scaleX = 30 / Math.max(...floorData.rooms.map(r => Math.abs(r.x_position)));
        const scaleZ = 30 / Math.max(...floorData.rooms.map(r => Math.abs(r.z_position)));

        return {
          id: room.id,
          type: room.type,
          // Scale and center the positions, keeping relative positions
          x: room.x_position * scaleX,
          y: room.z_position * scaleZ,
          width: room.width * scaleX,
          height: room.depth * scaleZ,
          name: room.name
        };
      });

      console.log('Transformed room data:', transformedRooms);
      return transformedRooms;
    } catch (error) {
      console.error('Error getting floor data:', error);
      return [];
    }
  }, [roomsData, floorName]);

  // Get room metrics and create color scale
  const { roomMetrics, getColor } = useMemo(() => {
    // Filter for room metrics of the selected type
    const roomMetrics = metrics.filter(m => 
      m.metric_name === selectedMetric && 
      m.room_id && // Make sure it's a room metric
      typeof m.value === 'number'
    );
    
    console.log('Filtered room metrics:', {
      selectedMetric,
      metrics,
      filteredMetrics: roomMetrics
    });

    if (roomMetrics.length === 0) {
      console.warn('No room metrics found for:', selectedMetric);
      // Return a function that returns a THREE.Color
      return { 
        roomMetrics: [], 
        getColor: () => new THREE.Color(selectedColor)
      };
    }

    // Create color scale based on metric values
    const values = roomMetrics.map(m => m.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    // Create a color scale function
    const getColor = (value: number) => {
      if (values.length === 0) return new THREE.Color(selectedColor);
      
      // Normalize the value between 0 and 1
      const normalizedValue = (value - min) / (max - min);
      
      // Create a color scale from white to the selected color
      const targetColor = new THREE.Color(selectedColor);
      const baseColor = new THREE.Color('#ffffff');
      
      // Ensure the color blending is visible
      return baseColor.lerp(targetColor, Math.max(0.2, normalizedValue));
    };
    
    return {
      roomMetrics,
      getColor
    };
  }, [metrics, selectedMetric, selectedColor]);

  // If no rooms are loaded, show a loading state
  if (floorRooms.length === 0) {
    return (
      <group>
        <mesh
          position={[0, 0, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
          receiveShadow
        >
          <planeGeometry args={[100, 100]} />
          <meshStandardMaterial color="#f0f0f0" />
        </mesh>
        <mesh position={[0, 2, 0]}>
          <boxGeometry args={[10, 1, 10]} />
          <meshStandardMaterial color="#cccccc" />
        </mesh>
      </group>
    );
  }

  return (
    <group>
      <mesh
        position={[0, 0, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        receiveShadow
      >
        <planeGeometry args={[30, 30]} />
        <meshStandardMaterial color="#f0f0f0" />
      </mesh>

      {floorRooms.map((room) => {
        // Find the metric value for this room
        const roomMetric = roomMetrics.find(m => m.room_id === room.id);
        const metricValue = roomMetric?.value;

        console.log('Room metric:', {
          roomId: room.id,
          metricValue,
          selectedMetric
        });

        return (
          <Room
            key={room.id}
            position={[room.x, 0.1, room.y]} // Slightly above the floor
            width={room.width}
            height={1}
            depth={room.height}
            roomId={room.id}
            roomType={room.type}
            value={metricValue}
            onRoomSelect={(id) => console.log('Room selected:', id)}
            getColorForValue={getColor}
          />
        );
      })}
    </group>
  );
}

export default FloorDetail;