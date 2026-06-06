import {
  ChangeDetectionStrategy, Component, input,
  effect, AfterViewInit, ElementRef, viewChild
} from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import * as L from 'leaflet';
import { RegionData } from '../../../core/models/region.model';

declare module 'leaflet' {
  function heatLayer(
    latlngs: Array<[number, number, number?]>,
    options?: {
      minOpacity?: number;
      maxZoom?: number;
      max?: number;
      radius?: number;
      blur?: number;
      gradient?: Record<number, string>;
    }
  ): L.Layer;
}

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
  private markersLayer: L.LayerGroup | null = null;
  private heatPluginLoaded = false;

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

  private async initMap() {
    const el = this.mapEl()?.nativeElement;
    if (!el) return;

    await this.loadHeatPlugin();

    this.map = L.map(el, {
      center: [-15.7801, -47.9292],
      zoom: 4,
    });

    L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      { attribution: '© OpenStreetMap © CARTO' }
    ).addTo(this.map);

    setTimeout(() => {
      this.map.invalidateSize();
      if (this.regions().length) {
        this.updateHeatmap(this.regions());
      }
    }, 200);
  }

  private async loadHeatPlugin(): Promise<void> {
    if (this.heatPluginLoaded) return;

    (window as unknown as Record<string, unknown>)['L'] = L;

    await import('leaflet.heat');
    this.heatPluginLoaded = true;
  }

  private updateHeatmap(data: RegionData[]) {
    if (this.heatLayer) {
      this.map.removeLayer(this.heatLayer);
      this.heatLayer = null;
    }
    if (this.markersLayer) {
      this.map.removeLayer(this.markersLayer);
      this.markersLayer = null;
    }

    const max = Math.max(...data.map(r => r.totalCases));

    const points = data.map(r => [
      r.latitude,
      r.longitude,
      r.totalCases / max
    ] as [number, number, number]);

    this.heatLayer = L.heatLayer(points, {
      radius: 35,
      blur: 25,
      gradient: { 0.2: '#00ff00', 0.5: '#ffff00', 0.75: '#ff6600', 1.0: '#ff0000' },
      minOpacity: 0.8
    }).addTo(this.map);

    this.markersLayer = L.layerGroup();
    data.forEach(r => {
      const marker = L.circleMarker([r.latitude, r.longitude], {
        radius: 8,
        fillColor: '#ff3333',
        color: '#ff3333',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.9
      });
      marker.bindPopup(`
        <strong>${r.city} — ${r.state}</strong><br/>
        Cases: ${r.totalCases}<br/>
        Symptoms: ${r.mainSymptoms ?? '—'}
      `);
      this.markersLayer!.addLayer(marker);
    });
    this.markersLayer.addTo(this.map);

    const epicenter = data[0];
    if (epicenter?.latitude != null && epicenter?.longitude != null) {
      this.map.flyTo([epicenter.latitude, epicenter.longitude], 6, { duration: 1 });
    }
  }
}