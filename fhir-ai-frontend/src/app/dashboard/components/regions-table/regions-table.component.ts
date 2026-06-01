import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { RegionData } from '../../../core/models/region.model';

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

  growthColor(growth: number): string {
    if (growth >= 70) return '#ff4d4f';
    if (growth >= 50) return '#ff7a45';
    if (growth >= 30) return '#faad14';
    return '#52c41a';
  }
}