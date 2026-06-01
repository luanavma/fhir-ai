import { ChangeDetectionStrategy, Component, input, computed } from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzStatisticModule } from 'ng-zorro-antd/statistic';
import { NzBadgeModule } from 'ng-zorro-antd/badge';
import { EpiKPIs } from '../../../core/models/epi-data.model';

@Component({
  selector: 'app-kpi-cards',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NzCardModule, NzStatisticModule, NzBadgeModule],
  templateUrl: './kpi-cards.component.html',
  styleUrls: ['./kpi-cards.component.css'],
})
export class KpiCardsComponent {

  kpis = input<EpiKPIs | null>(null);

  riskColor = computed(() => {
    const colors: Record<string, string> = {
      LOW: '#52c41a', MODERATE: '#faad14',
      HIGH: '#ff7a45', CRITICAL: '#ff4d4f',
    };
    return colors[this.kpis()?.riskLevel ?? ''] ?? '#fff';
  });
}