import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, delay } from 'rxjs';
import { AskResponse } from '../models/chat.model';
import { RegionData } from '../models/region.model';
import { AISummary } from '../models/ai-summary.model';

@Injectable({ providedIn: 'root' })
export class ChatService {

  private readonly http = inject(HttpClient);
  private readonly API = 'http://localhost:8080/fhir-agent';
  // private readonly chatId = crypto.randomUUID();


  ask(question: string): Observable<AskResponse> {
    const lower = question.toLowerCase();
    let answer = `Identifiquei 18 regiões com crescimento expressivo de reports compatíveis com diarreia e febre nos últimos 7 dias.\n\nDestaques principais:\n• São José do Rio Preto (SP): +78,4%\n• Ribeirão Preto (SP): +65,2%\n• Uberlândia (MG): +54,1%\n\nExpansão observada no interior de SP e MG.`;
    let regions: RegionData[] = [];
    let summary: AISummary | null = null;

    if (lower.includes('dengue')) {
      answer = `Foram identificados 234 casos de dengue nas últimas 2 semanas.\nRegiões com maior incidência: Campinas (SP), Ribeirão Preto (SP) e Uberlândia (MG).\nCódigos utilizados: ICD-10 A90, SNOMED 061462000.`;
      regions = [
        { city: 'Campinas', state: 'SP', totalCases: 80, mainSymptoms: 'febre, dor de cabeça', latitude: -22.90556, longitude: -47.06083 },
        { city: 'Ribeirão Preto', state: 'SP', totalCases: 90, mainSymptoms: 'febre, mialgia', latitude: -21.17746, longitude: -47.81031 },
        { city: 'Uberlândia', state: 'MG', totalCases: 64, mainSymptoms: 'febre, dor abdominal', latitude: -18.9126, longitude: -48.2754 },
      ];

      summary = {
        text: 'Casos compatíveis com dengue concentrados em Campinas, Ribeirão Preto e Uberlândia.',
        recommendations: ['Notificar casos', 'Intensificar controle vetorial', 'Orientar população']
      };

    } else if (lower.includes('risco') || lower.includes('alerta')) {
      answer = `O risco epidemiológico atual é ALTO.\n18 regiões estão em alerta, com crescimento médio de 41,7% comparado aos 7 dias anteriores.`;
      regions = [
        { city: 'São José do Rio Preto', state: 'SP', totalCases: 120, mainSymptoms: 'diarreia, febre', latitude: -20.8196, longitude: -49.3798 },
        { city: 'Ribeirão Preto', state: 'SP', totalCases: 98, mainSymptoms: 'diarreia, febre', latitude: -21.17746, longitude: -47.81031 },
        { city: 'Uberlândia', state: 'MG', totalCases: 76, mainSymptoms: 'febre, vômito', latitude: -18.9126, longitude: -48.2754 },
      ];

    } else if (lower.includes('recomend')) {
      answer = `Com base nos dados atuais:\n1. Notificar vigilância sanitária das 18 regiões em alerta\n2. Reforçar orientações sobre higiene e água tratada\n3. Monitorar pacientes nas UBSs`;
      summary = {
        text: 'Recomendações operacionais baseadas nos alertas atuais.',
        recommendations: ['Notificar vigilância', 'Reforçar higiene', 'Monitorar nas UBSs']
      };
    } else {
      regions = [
        { city: 'São José do Rio Preto', state: 'SP', totalCases: 150, mainSymptoms: 'diarreia, febre', latitude: -20.8196, longitude: -49.3798 },
        { city: 'Ribeirão Preto', state: 'SP', totalCases: 110, mainSymptoms: 'diarreia, febre', latitude: -21.17746, longitude: -47.81031 },
        { city: 'Uberlândia', state: 'MG', totalCases: 95, mainSymptoms: 'diarreia, febre', latitude: -18.9126, longitude: -48.2754 },
      ];
    }

    const response: AskResponse = { answer, regions, summary };
    return of(response).pipe(delay(1200));
  }


  // ask(question: string): Observable<AskResponse> {
  //   const body: AskRequest = {
  //     chatId: this.chatId,
  //     question
  //   };
  //   return this.http.post<AskResponse>(`${this.API}/ask`, body);
  // }
}