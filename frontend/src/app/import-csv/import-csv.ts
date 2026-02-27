import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as Papa from 'papaparse';

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

  constructor(private cdr: ChangeDetectorRef) {}

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
      encoding: 'windows-1251',
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
    if (!this.isParsed || !this.previewData.length) return;

    console.log('Відправляємо дані на локальний бек...', this.previewData);

    // Припустимо, твій бек чекає POST запит
    // this.http.post('http://localhost:8000/api/orders', this.previewData)
    //   .subscribe(res => console.log('Збережено!'));

    alert('Дані готові до відправки на локальний сервер!');
  }

  reset() {
    this.selectedFile = null;
    this.isParsed = false;
    this.previewData = [];
    this.headers = [];
    this.tableLetters = [];
  }
}
