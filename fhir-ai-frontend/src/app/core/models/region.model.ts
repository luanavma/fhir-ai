export interface RegionData {
  city: string;
  state?: string;
  totalCases: number;
  mainSymptoms: string | null;
  latitude: number;
  longitude: number;
  similarity?: number;
}