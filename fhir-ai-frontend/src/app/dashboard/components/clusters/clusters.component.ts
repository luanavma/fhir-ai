import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { Cluster } from '../../../core/models/cluster.model';

@Component({
  selector: 'app-clusters',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NzCardModule, NzTagModule],
  templateUrl: './clusters.component.html',
  styleUrls: ['./clusters.component.css'],
})
export class ClustersComponent {
  clusters = input<Cluster[]>([]);
}