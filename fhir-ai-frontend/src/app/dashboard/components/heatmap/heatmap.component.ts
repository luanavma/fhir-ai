import {
  ChangeDetectionStrategy, Component, input,
  effect, AfterViewInit, ElementRef, viewChild
} from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import * as L from 'leaflet';
import 'leaflet.heat';
import { RegionData } from '../../../core/models/region.model';

@Component({
  selector: 'app-heatmap',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NzCardModule],
  templateUrl: './heatmap.component.html',
})
export class HeatmapComponent implements AfterViewInit {

  regions = input<RegionData[]>([]);

  private mapEl = viewChild<ElementRef>('mapEl');
  private map!: L.Map;
  private heatLayer: L.Layer | null = null;

  constructor() {
    effect(() => {
      const data = this.regions();
      if (this.map && data.length) {
        this.updateHeatmap(data);
      }
    });
  }

  ngAfterViewInit() {
    setTimeout(() => this.initMap(), 100);
  }

  private initMap() {
    const el = this.mapEl()?.nativeElement;
    if (!el) return;

    this.map = L.map(el, {
      center: [-15.7801, -47.9292],
      zoom: 4,
    });

    L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      { attribution: '© OpenStreetMap © CARTO' }
    ).addTo(this.map);

    if (this.regions().length) {
      this.updateHeatmap(this.regions());
    }
  }

  private updateHeatmap(data: RegionData[]) {
    if (this.heatLayer) {
      this.map.removeLayer(this.heatLayer);
    }

    const max = Math.max(...data.map(r => r.growth));

    const points = data.map(r => [
      r.latitude, r.longitude, r.growth / max
    ] as [number, number, number]);

    this.heatLayer = (L as unknown as Record<string, CallableFunction>)
      ['heatLayer'](points, {
        radius: 40, blur: 30,
        gradient: { 0.2: '#00ff00', 0.5: '#ffff00', 0.75: '#ff6600', 1.0: '#ff0000' },
      })
      .addTo(this.map);
  }
}