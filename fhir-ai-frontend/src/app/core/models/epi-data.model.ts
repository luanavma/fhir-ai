export interface EpiKPIs {
  regionsInAlert: number;
  regionsInAlertDelta: number;
  averageGrowth: number;
  totalReports: number;
  mainSymptom: string;
  riskLevel: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
}