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
  loading = signal(false);
  currentMessage = '';
  private shouldScroll = false;
  suggestions = [
    'Dengue cases by region this week',
    'Which regions have the most respiratory cases?',
    'Show gastrointestinal outbreak patterns',
  ];

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  useSuggestion(suggestion: string) {
    this.currentMessage = suggestion;
    this.sendMessage();
  }

  sendMessage() {
    const question = this.currentMessage.trim();
    if (!question || this.loading()) {
      return;
    }
    this.currentMessage = '';
    this.appendMessage(question, 'user');
    this.loading.set(true);
    this.shouldScroll = true;

    this.chatService.ask(question).subscribe({
      next: (res: AskResponse) => {
        this.appendMessage(res.answer, 'assistant');
        this.emitRegionsUpdate(res.regions);
        this.emitSummaryUpdate(res.summary!);
        this.loading.set(false);
        this.shouldScroll = true;
      },
      error: () => {
        this.appendConnectionErrorMessage();
        this.loading.set(false);
      },
    });
  }

  private scrollToBottom() {
    const el = this.scrollEl()?.nativeElement;
    if (el) el.scrollTop = el.scrollHeight;
  }

  private appendMessage(content: string, role: 'user' | 'assistant') {
    this.messages.update(msgs => [
      ...msgs,
      { role, content, timestamp: new Date() }
    ]);
  }

  private emitRegionsUpdate(regions: RegionData[]) {
    if (regions?.length) {
      this.regionsUpdated.emit(regions);
    }
  }

  private emitSummaryUpdate(summary: AISummary) {
    this.summaryUpdated.emit(summary);
  }

  private appendConnectionErrorMessage() {
    this.messages.update(msgs => [
      ...msgs,
      {
        role: 'assistant',
        content: 'Error connecting to server. Please try again.',
        timestamp: new Date()
      }
    ]);
  }


}