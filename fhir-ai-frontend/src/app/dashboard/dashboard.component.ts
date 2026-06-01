import {
  ChangeDetectionStrategy, Component, OnInit, signal, computed, inject
} from '@angular/core';
import { EpiKPIs } from '../core/models/epi-data.model';
import { RegionData } from '../core/models/region.model';
import { Cluster } from '../core/models/cluster.model';
import { AISummary } from '../core/models/ai-summary.model';
import { EpiDataService } from '../core/services/epi.service';
import { KpiCardsComponent } from './components/kpi-cards/kpi-cards.component';
import { AiSummaryComponent } from './components/ai-summary/ai-summary.component';
import { HeatmapComponent } from './components/heatmap/heatmap.component';
import { RegionsTableComponent } from './components/regions-table/regions-table.component';
import { ClustersComponent } from './components/clusters/clusters.component';
import { EpiChatComponent } from './components/epi-chat/epi-chat.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    KpiCardsComponent, AiSummaryComponent, HeatmapComponent, RegionsTableComponent, ClustersComponent, EpiChatComponent
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css'],
})
export class DashboardComponent implements OnInit {

  private readonly epiService = inject(EpiDataService);

  kpis = signal<EpiKPIs | null>(null);
  regions = signal<RegionData[]>([]);
  clusters = signal<Cluster[]>([]);
  summary = signal<AISummary | null>(null);

  ngOnInit() {
    this.epiService.getKPIs().subscribe(v => this.kpis.set(v));
    this.epiService.getRegions().subscribe(v => this.regions.set(v));
    this.epiService.getClusters().subscribe(v => this.clusters.set(v));
    this.epiService.getAISummary().subscribe(v => this.summary.set(v));
  }
}