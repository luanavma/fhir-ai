import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { AISummary } from '../../../core/models/ai-summary.model';

@Component({
  selector: 'app-ai-summary',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NzCardModule, NzTagModule],
  templateUrl: './ai-summary.component.html',
  styleUrls: ['./ai-summary.component.css'],
})
export class AiSummaryComponent {
  summary = input<AISummary | null>(null);
}