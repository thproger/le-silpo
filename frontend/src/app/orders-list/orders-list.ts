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

  constructor(
    private http: HttpClient,
    private cdr: ChangeDetectorRef,
  ) {}

  currentSort = {
    column: 'timestamp',
    direction: 'newest',
  };

  get totalPages() {
    return Math.ceil(this.totalItems / this.pageSize) || 1;
  }

  loadOrders(): void {
    const offset = (this.currentPage - 1) * this.pageSize;

    let params = new HttpParams()
      .set('limit', this.pageSize.toString())
      .set('offset', offset.toString())
      .set('sort_by', this.currentSort.column)
      .set('order', this.currentSort.direction === 'newest' ? 'desc' :
        this.currentSort.direction === 'oldest' ? 'asc' :
          this.currentSort.direction);

    this.http.get<any>(`https://le-silpo-production.up.railway.app/orders`, { params }).subscribe({
      next: (response) => {
        this.pagedOrders = [...response.data];
        this.totalItems = response.total;
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error:', err),
    });
  }

  goToPage(page: number): void {
    this.currentPage = page;
    this.loadOrders();
  }

  applyFilters() {
    this.currentPage = 1;
    this.loadOrders();
  }

  toggleFilters() {
    this.showFilterRow = !this.showFilterRow;
  }

  updateSort(column: string, direction: string) {
    this.currentSort = { column, direction };
    this.applyFilters();
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
