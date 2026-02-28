import { Component, AfterViewInit } from '@angular/core';
import { FormArray, FormBuilder, FormGroup } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import * as L from 'leaflet';

const NY_STATE_BOUNDS = L.latLngBounds(
  L.latLng(40.47, -79.76),
  L.latLng(45.01, -71.85),
);

@Component({
  selector: 'app-manual-create',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './manual-create.html',
  styleUrl: './manual-create.css',
})
export class ManualCreate {
  orderForm: FormGroup;
  isMapVisible = false;
  currentRowIndex: number = 0;
  private map?: L.Map;

  constructor(private fb: FormBuilder) {
    this.orderForm = this.fb.group({
      rows: this.fb.array([this.createRow()]),
    });
  }

  get rows() {
    return this.orderForm.get('rows') as FormArray;
  }

  createRow() {
    return this.fb.group({
      longitude: [''],
      latitude: [''],
      timestamp: [''],
      subtotal: [''],
      tax: [''],
      total: [''],
    });
  }

  addRow() {
    this.rows.push(this.createRow());
  }

  openMap(index: number) {
    this.currentRowIndex = index;
    this.isMapVisible = true;

    setTimeout(() => {
      this.initMap();
    }, 10);
  }

  closeMap() {
    this.isMapVisible = false;

    if (this.map) {
      this.map.off();
      this.map.remove();
      this.map = undefined;
    }
  }

  private initMap() {
    if (this.map) {
      this.map.remove();
    }

    this.map = L.map('map-container', {
      maxBounds: NY_STATE_BOUNDS, // Обмежуємо виїзд за межі штату
      maxBoundsViscosity: 0.8,    // Даємо трохи "м'якості" при досягненні меж
      minZoom: 6,                 // Щоб не можна було віддалитися до вигляду всього світу
    }).setView([42.8, -75.5], 7); // Центруємо мапу по центру штату NY

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap'
    }).addTo(this.map);

    L.rectangle(NY_STATE_BOUNDS, {
      color: "#ff7800",
      weight: 1,
      fill: false,
      interactive: false
    }).addTo(this.map);

    this.map.on('click', (e: L.LeafletMouseEvent) => {
      const { lat, lng } = e.latlng;

      // Перевірка, чи клікнули саме в штаті (бо рамка прямокутна, а штат має складну форму)
      if (NY_STATE_BOUNDS.contains(e.latlng)) {
        this.rows.at(this.currentRowIndex).patchValue({
          latitude: lat.toFixed(6),
          longitude: lng.toFixed(6)
        });
        this.closeMap();
      }
    });

    setTimeout(() => this.map?.invalidateSize(), 200);
  }
}
