import { Component, AfterViewInit } from '@angular/core';
import { FormArray, FormBuilder, FormGroup } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import * as L from 'leaflet';
import { HttpClient } from '@angular/common/http';
import { Validators } from '@angular/forms';

const NY_STATE_BOUNDS = L.latLngBounds(L.latLng(40.47, -79.76), L.latLng(45.01, -71.85));

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

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
  ) {
    this.orderForm = this.fb.group({
      rows: this.fb.array([this.createRow()]),
    });
  }

  get rows() {
    return this.orderForm.get('rows') as FormArray;
  }

  createRow() {
    return this.fb.group({
      longitude: ['', Validators.required],
      latitude: ['', Validators.required],
      timestamp: [new Date().toISOString().slice(0, 19).replace('T', ' ')],
      subtotal: [0, [Validators.required, Validators.min(0)]],
      tax: [0],
      total: [0],
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
      maxBounds: NY_STATE_BOUNDS,
      maxBoundsViscosity: 0.8,
      minZoom: 6,
    }).setView([42.8, -75.5], 7);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap',
    }).addTo(this.map);

    L.rectangle(NY_STATE_BOUNDS, {
      color: '#ff7800',
      weight: 1,
      fill: false,
      interactive: false,
    }).addTo(this.map);

    this.map.on('click', (e: L.LeafletMouseEvent) => {
      const { lat, lng } = e.latlng;

      if (NY_STATE_BOUNDS.contains(e.latlng)) {
        this.rows.at(this.currentRowIndex).patchValue({
          latitude: lat.toFixed(6),
          longitude: lng.toFixed(6),
        });
        this.closeMap();
      }
    });

    setTimeout(() => this.map?.invalidateSize(), 200);
  }

  submitRow(index: number) {
    const rowValue = this.rows.at(index).value;

    const payload = {
      latitude: parseFloat(rowValue.latitude),
      longitude: parseFloat(rowValue.longitude),
      subtotal: parseFloat(rowValue.subtotal),
      timestamp: rowValue.timestamp || new Date().toISOString().slice(0, 19).replace('T', ' ')
    };

    this.http.post('https://le-silpo-production.up.railway.app/orders', payload).subscribe({
      next: (response) => {
        console.log('Успішно збережено:', response);
        alert('Замовлення додано!');
      },
      error: (error) => {
        console.error('Помилка при збереженні:', error);
        alert('Сервер повернув помилку. Перевір консоль.');
      }
    });
  }
}
