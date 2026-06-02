import {
  ChangeDetectionStrategy, Component, signal} from '@angular/core';
import { RegionData } from '../core/models/region.model';
import { AISummary } from '../core/models/ai-summary.model';
import { AiSummaryComponent } from './components/ai-summary/ai-summary.component';
import { HeatmapComponent } from './components/heatmap/heatmap.component';
import { RegionsTableComponent } from './components/regions-table/regions-table.component';
import { EpiChatComponent } from './components/epi-chat/epi-chat.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    AiSummaryComponent, HeatmapComponent, RegionsTableComponent, EpiChatComponent
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent {

  regions = signal<RegionData[]>([]);
  summary = signal<AISummary | null>(null);

}