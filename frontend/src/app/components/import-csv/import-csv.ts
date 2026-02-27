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

  constructor(private cdr: ChangeDetectorRef) {} // Додаємо для надійності оновлення UI

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
      skipEmptyLines: true,
      preview: 10,
      complete: (result) => {
        this.headers = result.meta.fields || [];
        this.previewData = result.data;
        this.tableLetters = this.headers.map((_, i) => String.fromCharCode(65 + i));
        this.isParsed = true;
        this.cdr.detectChanges(); // Примусово оновлюємо екран
      }
    });
  }

  reset() {
    this.selectedFile = null;
    this.isParsed = false;
    this.previewData = [];
    this.headers = [];
    this.tableLetters = [];
  }
}