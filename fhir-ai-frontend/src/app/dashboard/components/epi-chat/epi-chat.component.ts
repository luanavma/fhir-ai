import {
  ChangeDetectionStrategy, Component, signal,
  inject, AfterViewChecked, viewChild, ElementRef,
  output
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzAvatarModule } from 'ng-zorro-antd/avatar';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { AskResponse, ChatMessage } from '../../../core/models/chat.model';
import { ChatService } from '../../../core/services/chat.service';
import { AISummary } from '../../../core/models/ai-summary.model';
import { RegionData } from '../../../core/models/region.model';

@Component({
  selector: 'app-epi-chat',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    FormsModule, NzCardModule, NzInputModule,
    NzButtonModule, NzSpinModule, NzAvatarModule, NzIconModule,
  ],
  templateUrl: './epi-chat.component.html',
  styleUrls: ['./epi-chat.component.css'],
})
export class EpiChatComponent implements AfterViewChecked {

  private readonly chatService = inject(ChatService);
  private scrollEl = viewChild<ElementRef>('scrollEl');

  regionsUpdated = output<RegionData[]>();
  summaryUpdated = output<AISummary>();

  messages = signal<ChatMessage[]>([]);
  loading  = signal(false);
  currentMessage = '';
  private shouldScroll = false;

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  sendMessage() {
    const question = this.currentMessage.trim();
    if (!question || this.loading()) return;

    this.currentMessage = '';
    this.messages.update(msgs => [
      ...msgs,
      { role: 'user', content: question, timestamp: new Date() }
    ]);

    this.loading.set(true);
    this.shouldScroll = true;

    this.chatService.ask(question).subscribe({
      next: (res: AskResponse) => {

        this.messages.update(msgs => [
          ...msgs,
          { role: 'assistant', content: res.answer, timestamp: new Date() }
        ]);

        // emite regiões pro mapa e tabela
        if (res.regions?.length) {
          this.regionsUpdated.emit(res.regions);
        }

        // emite summary pro card de resumo
        if (res.summary) {
          this.summaryUpdated.emit(res.summary);
        }

        this.loading.set(false);
        this.shouldScroll = true;
      },
      error: () => {
        this.messages.update(msgs => [
          ...msgs,
          {
            role: 'assistant',
            content: 'Erro ao conectar com o servidor. Tente novamente.',
            timestamp: new Date()
          }
        ]);
        this.loading.set(false);
      },
    });
  }

  private scrollToBottom() {
    const el = this.scrollEl()?.nativeElement;
    if (el) el.scrollTop = el.scrollHeight;
  }
}