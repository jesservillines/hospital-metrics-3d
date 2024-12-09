import Papa from 'papaparse';

export interface RoomProperties {
  maxOccupancy: number;
  hasOxygen: boolean;
  hasTelemetry: boolean;
  isNegativePressure: boolean;
  isIsolation: boolean;
  equipmentList: string[];
  specialFeatures?: string[];
  squareFootage: number;
  windowCount: number;
}

export interface RoomMetrics {
  occupancy: number;
  nurseResponseTime: number;
  patientSatisfaction: number;
  equipmentUtilization: number;
  lastCleaned: Date;
  temperatureF: number;
  humidityPercent: number;
  co2Level: number;
}

export interface Room {
  id: string;
  floor: string;
  type: 'patient' | 'therapy' | 'nurse' | 'office' | 'hallway';
  name: string;
  width: number;
  depth: number;
  x_position: number;
  z_position: number;
  notes?: string;
  properties: Partial<RoomProperties>;
  metrics?: Partial<RoomMetrics>;
}

export interface FloorData {
  floorName: string;
  rooms: Room[];
  metrics: {
    avgOccupancy: number;
    avgResponseTime: number;
    totalPatients: number;
    staffCount: number;
  };
}

// Default properties for different room types
const defaultRoomProperties: Record<Room['type'], Partial<RoomProperties>> = {
  patient: {
    maxOccupancy: 1,
    hasOxygen: true,
    hasTelemetry: true,
    isNegativePressure: false,
    isIsolation: false,
    equipmentList: ['Hospital Bed', 'Patient Monitor', 'IV Pump'],
    squareFootage: 240,
    windowCount: 1
  },
  therapy: {
    maxOccupancy: 10,
    hasOxygen: true,
    equipmentList: ['Parallel Bars', 'Exercise Mats', 'Training Stairs'],
    squareFootage: 1200,
    windowCount: 4
  },
  nurse: {
    maxOccupancy: 4,
    equipmentList: ['Medication Cart', 'Computer Workstations'],
    squareFootage: 400,
    windowCount: 0
  },
  office: {
    maxOccupancy: 2,
    equipmentList: ['Desk', 'Computer'],
    squareFootage: 150,
    windowCount: 1
  },
  hallway: {
    maxOccupancy: 20,
    equipmentList: ['Crash Cart'],
    squareFootage: 500,
    windowCount: 0
  }
};

class RoomDataService {
  private floors: Map<string, FloorData> = new Map();
  private rooms: Map<string, Room> = new Map();

  async loadFromCSV(csvUrl: string): Promise<void> {
    try {
      const response = await fetch(csvUrl);
      const csvText = await response.text();

      const { data } = Papa.parse(csvText, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true
      });

      this.processRoomData(data);
    } catch (error) {
      console.error('Error loading room data:', error);
      throw error;
    }
  }

  private processRoomData(data: any[]): void {
    // Group rooms by floor
    const floorGroups = new Map<string, any[]>();

    data.forEach(row => {
      const floorName = row.floor;
      if (!floorGroups.has(floorName)) {
        floorGroups.set(floorName, []);
      }
      floorGroups.get(floorName)!.push(row);
    });

    // Process each floor
    floorGroups.forEach((roomsData, floorName) => {
      const rooms: Room[] = roomsData.map(row => this.createRoom(row));

      const floorData: FloorData = {
        floorName,
        rooms,
        metrics: this.calculateFloorMetrics(rooms)
      };

      this.floors.set(floorName, floorData);
      rooms.forEach(room => this.rooms.set(room.id, room));
    });
  }

  private createRoom(data: any): Room {
    const type = data.room_type as Room['type'];
    const baseProperties = defaultRoomProperties[type];

    return {
      id: data.room_id,
      floor: data.floor,
      type,
      name: data.room_name,
      width: data.width,
      depth: data.depth,
      x_position: data.x_position,
      z_position: data.z_position,
      notes: data.notes,
      properties: {
        ...baseProperties,
        // Add any custom properties from CSV
      }
    };
  }

  private calculateFloorMetrics(rooms: Room[]): FloorData['metrics'] {
    const patientRooms = rooms.filter(r => r.type === 'patient');

    return {
      avgOccupancy: 0.85, // Example values
      avgResponseTime: 5.2,
      totalPatients: patientRooms.length,
      staffCount: Math.ceil(patientRooms.length / 4)
    };
  }

  getFloor(floorName: string): FloorData | undefined {
    return this.floors.get(floorName);
  }

  getRoom(roomId: string): Room | undefined {
    return this.rooms.get(roomId);
  }

  updateRoomMetrics(roomId: string, metrics: Partial<RoomMetrics>): void {
    const room = this.rooms.get(roomId);
    if (room) {
      room.metrics = { ...room.metrics, ...metrics };
    }
  }

  getFloorMetrics(floorName: string): Array<{ roomId: string; metrics: Partial<RoomMetrics> }> {
    const floor = this.floors.get(floorName);
    if (!floor) return [];

    return floor.rooms
      .filter(room => room.metrics)
      .map(room => ({
        roomId: room.id,
        metrics: room.metrics!
      }));
  }

  getRoomsByType(floorName: string, type: Room['type']): Room[] {
    const floor = this.floors.get(floorName);
    if (!floor) return [];

    return floor.rooms.filter(room => room.type === type);
  }

  searchRooms(query: string): Room[] {
    const lowerQuery = query.toLowerCase();
    return Array.from(this.rooms.values()).filter(room =>
      room.name.toLowerCase().includes(lowerQuery) ||
      room.id.toLowerCase().includes(lowerQuery)
    );
  }
}

export const roomDataService = new RoomDataService();
export default roomDataService;