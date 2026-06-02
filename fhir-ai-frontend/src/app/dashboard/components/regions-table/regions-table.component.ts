import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { RegionData } from '../../../core/models/region.model';

const SIMILARITY_MOCK: Record<string, number> = {
  'RECIFE': 1.0,
  'MANAUS': 0.91,
  'BELO HORIZONTE': 0.88,
  'RIBEIRAO PRETO': 0.84,
  'SALVADOR': 0.81,
  'CAMPINAS': 0.76,
  'UBERLANDIA': 0.74,
  'RIO DE JANEIRO': 0.71,
  'SAO JOSE DO RIO PRETO': 0.65,
  'SAO PAULO': 0.61,
};

@Component({
  selector: 'app-regions-table',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NzCardModule, NzTableModule, NzTagModule],
  templateUrl: './regions-table.component.html',
  styleUrls: ['./regions-table.component.css'],
})
export class RegionsTableComponent {

  regions = input<RegionData[]>([]);
  topRegion = computed(() => this.regions()[0] ?? null);

  similarRegions = computed(() =>
    this.regions().slice(1).map(r => ({
      ...r,
      similarity: r.similarity ?? SIMILARITY_MOCK[r.city] ?? undefined
    }))
  );

  similarityColor(similarity?: number): string {
    if (!similarity) return '#8b949e';
    if (similarity >= 0.85) return '#ff4d4f';
    if (similarity >= 0.70) return '#ff7a45';
    return '#faad14';
  }

  similarityTagColor(similarity?: number): string {
    if (!similarity) return 'default';
    if (similarity >= 0.85) return 'red';
    if (similarity >= 0.70) return 'orange';
    return 'gold';
  }

}