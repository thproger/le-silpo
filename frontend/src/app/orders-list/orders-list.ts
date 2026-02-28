import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-orders-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './orders-list.html',
  styleUrls: ['./orders-list.css'],
})
export class OrdersList implements OnInit {
  pagedOrders: any[] = [];
  currentPage = 1;
  pageSize = 10;
  totalItems = 0;
  showFilterRow = false;

  columnFilters = {
    longitude: '',
    latitude: '',
    subtotal: '',
    tax: ''
  };

  constructor(
    private http: HttpClient,
    private cdr: ChangeDetectorRef,
  ) {}

  get totalPages() {
    return Math.ceil(this.totalItems / this.pageSize) || 1;
  }

  loadOrders(): void {
    const offset = (this.currentPage - 1) * this.pageSize;

    let params = new HttpParams()
      .set('limit', this.pageSize.toString())
      .set('offset', offset.toString());

    if (this.columnFilters.longitude) params = params.set('longitude', this.columnFilters.longitude);
    if (this.columnFilters.latitude) params = params.set('latitude', this.columnFilters.latitude);
    if (this.columnFilters.subtotal) params = params.set('subtotal', this.columnFilters.subtotal);

    this.http
      .get<any>(`https://le-silpo-production.up.railway.app/orders`, {
        params,
      })
      .subscribe({
        next: (response) => {
          this.pagedOrders = response.data;
          this.totalItems = response.total;
          this.cdr.detectChanges();
        },
        error: (err) => console.error('Помилка завантаження:', err),
      });
  }

  goToPage(page: number): void {
    this.currentPage = page;
    this.loadOrders();
  }

  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadOrders();
    }
  }

  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadOrders();
    }
  }

  applyFilters() {
    this.currentPage = 1;
    this.loadOrders();
  }

  toggleFilters() {
    this.showFilterRow = !this.showFilterRow;
  }

  get visiblePages(): number[] {
    const pages = [];
    const start = Math.max(1, this.currentPage - 2);
    const end = Math.min(this.totalPages, start + 4);
    for (let i = start; i <= end; i++) pages.push(i);
    return pages;
  }

  ngOnInit(): void {
    this.loadOrders();
  }
}