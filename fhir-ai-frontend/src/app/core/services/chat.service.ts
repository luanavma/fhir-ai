import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, delay } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ChatService {

  private readonly http = inject(HttpClient);
  private readonly API = 'http://localhost:8080/fhir-agent';
  // private readonly chatId = crypto.randomUUID();


  ask(question: string): Observable<{ answer: string }> {
    const lower = question.toLowerCase();
    let answer = `Identifiquei 18 regiões com crescimento expressivo de reports compatíveis com diarreia e febre nos últimos 7 dias.\n\nDestaques principais:\n• São José do Rio Preto (SP): +78,4%\n• Ribeirão Preto (SP): +65,2%\n• Uberlândia (MG): +54,1%\n\nExpansão observada no interior de SP e MG.`;

    if (lower.includes('dengue')) {
      answer = `Foram identificados 234 casos de dengue nas últimas 2 semanas.\nRegiões com maior incidência: Campinas (SP), Ribeirão Preto (SP) e Uberlândia (MG).\nCódigos utilizados: ICD-10 A90, SNOMED 061462000.`;
    } else if (lower.includes('risco') || lower.includes('alerta')) {
      answer = `O risco epidemiológico atual é ALTO.\n18 regiões estão em alerta, com crescimento médio de 41,7% comparado aos 7 dias anteriores.`;
    } else if (lower.includes('recomend')) {
      answer = `Com base nos dados atuais:\n1. Notificar vigilância sanitária das 18 regiões em alerta\n2. Reforçar orientações sobre higiene e água tratada\n3. Monitorar pacientes nas UBSs`;
    }

    return of({ answer }).pipe(delay(1200));
  }


  // ask(question: string): Observable<AskResponse> {
  //   const body: AskRequest = {
  //     chatId: this.chatId,
  //     question
  //   };
  //   return this.http.post<AskResponse>(`${this.API}/ask`, body);
  // }
}