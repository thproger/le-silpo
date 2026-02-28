import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as Papa from 'papaparse';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { OrderService } from '../services/order';

@Component({
  selector: 'app-import-csv',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './import-csv.html',
  styleUrl: './import-csv.css',
})
export class ImportCsv {
  selectedFile: File | null = null;
  previewData: any[] = [];
  headers: string[] = [];
  tableLetters: string[] = [];
  isParsed: boolean = false;
  isDragging: boolean = false;
  result: any[] = [];

  constructor(
    private cdr: ChangeDetectorRef,
    private http: HttpClient,
    private orderService: OrderService,
    private router: Router,
  ) {}

  onFileSelected(event: any) {
    let file: File | null = null;
    if (event.target.files && event.target.files.length > 0) {
      file = event.target.files[0];
    } else if (event.dataTransfer && event.dataTransfer.files.length > 0) {
      file = event.dataTransfer.files[0];
    }

    if (file) this.processFile(file);
  }

  processFile(file: File) {
    this.selectedFile = file;
    Papa.parse(file, {
      header: true,
      skipEmptyLines: 'greedy',
      encoding: 'utf-8',
      complete: (result) => {
        this.headers = result.meta.fields || [];
        this.previewData = result.data;
        this.tableLetters = this.headers.map((_, i) => String.fromCharCode(65 + i));
        this.isParsed = true;
        this.cdr.detectChanges();
      },
    });
  }

  uploadData() {
    if (this.selectedFile) {
      const formData = new FormData();
      formData.append('file', this.selectedFile, this.selectedFile.name);

      this.http.post('https://le-silpo-production.up.railway.app/orders/import', formData)
        .subscribe({
          next: () => {
            this.router.navigate(['/list']);
          },
          error: (err) => console.error('Помилка завантаження:', err)
        });
    }
  }

  reset() {
    this.selectedFile = null;
    this.isParsed = false;
    this.previewData = [];
    this.headers = [];
    this.tableLetters = [];
  }
}
