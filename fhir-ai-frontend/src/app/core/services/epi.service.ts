// dashboard/services/epi-data.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Cluster } from '../models/cluster.model';
import { RegionData } from '../models/region.model';
import { EpiKPIs } from '../models/epi-data.model';
import { AISummary } from '../models/ai-summary.model';

@Injectable({ providedIn: 'root' })
export class EpiDataService {

  private readonly http = inject(HttpClient);
  private readonly API = 'http://localhost:8080/api/epi';

  getKPIs(): Observable<EpiKPIs> {
    return of({
      regionsInAlert: 18,
      regionsInAlertDelta: 3,
      averageGrowth: 41.7,
      totalReports: 8431,
      mainSymptom: 'Diarreia, Febre + Dor abdominal',
      riskLevel: 'HIGH'
    } as EpiKPIs);
  }

  getRegions(days = 7): Observable<RegionData[]> {
    return of([
      { city: 'São José do Rio Preto', state: 'SP', growth: 78.4, totalCases: 342, mainSymptoms: 'Diarreia, Febre, Dor abdominal', latitude: -20.8197, longitude: -49.3794 },
      { city: 'Ribeirão Preto',        state: 'SP', growth: 65.2, totalCases: 287, mainSymptoms: 'Diarreia, Febre, Vômito',        latitude: -21.1775, longitude: -47.8103 },
      { city: 'Uberlândia',            state: 'MG', growth: 54.1, totalCases: 231, mainSymptoms: 'Diarreia, Febre',                latitude: -18.9186, longitude: -48.2772 },
      { city: 'Campinas',              state: 'SP', growth: 49.3, totalCases: 412, mainSymptoms: 'Diarreia, Dor abdominal',        latitude: -22.9056, longitude: -47.0608 },
      { city: 'Salvador',              state: 'BA', growth: 47.8, totalCases: 309, mainSymptoms: 'Diarreia, Febre, Náusea',        latitude: -12.9714, longitude: -38.5014 },
      { city: 'Fortaleza',             state: 'CE', growth: 38.2, totalCases: 198, mainSymptoms: 'Febre, Dor abdominal',           latitude:  -3.7172, longitude: -38.5433 },
      { city: 'Goiânia',               state: 'GO', growth: 35.6, totalCases: 176, mainSymptoms: 'Diarreia, Febre',                latitude: -16.6869, longitude: -49.2648 },
      { city: 'Manaus',                state: 'AM', growth: 29.4, totalCases: 143, mainSymptoms: 'Febre, Vômito',                  latitude:  -3.1190, longitude: -60.0217 },
      { city: 'Recife',                state: 'PE', growth: 27.1, totalCases: 167, mainSymptoms: 'Diarreia, Náusea',               latitude:  -8.0476, longitude: -34.8770 },
      { city: 'Curitiba',              state: 'PR', growth: 22.3, totalCases: 134, mainSymptoms: 'Febre, Dor abdominal',           latitude: -25.4284, longitude: -49.2733 },
    ]);
  }

  getClusters(): Observable<Cluster[]> {
    return of([
      { id: 1, symptoms: 'Diarreia + Febre + Dor abdominal', regions: 18, totalReports: 1284, similarity: 0.91 },
      { id: 2, symptoms: 'Vômito + Febre + Dor abdominal',   regions: 12, totalReports: 842,  similarity: 0.87 },
      { id: 3, symptoms: 'Diarreia + Dor abdominal',         regions: 9,  totalReports: 623,  similarity: 0.82 },
    ]);
  }

  getAISummary(): Observable<AISummary> {
    return of({
      text: 'Foi identificado aumento anormal de reports compatíveis com síndrome gastrointestinal em 18 regiões do país. O padrão sugere possível surto em expansão, principalmente no interior de São Paulo e Minas Gerais. Recomenda-se monitoramento intensificado nas próximas 48 horas.',
      recommendations: [
        'Monitorar evolução nas próximas 48 horas',
        'Comparar com histórico das últimas 4 semanas',
        'Validar concentração por unidade de atendimento',
      ],
      generatedAt: new Date(),
    });
  }
}