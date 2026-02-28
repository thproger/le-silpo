import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpParams } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface FilterState {
  tax: 'min' | 'max';
  timestamp: 'newest' | 'oldest';
  amount: 'min' | 'max';
}

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

  filters: FilterState = {
    tax: 'max',
    timestamp: 'newest',
    amount: 'max'
  };

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadOrders();
  }

  loadOrders(): void {
    const offset = (this.currentPage - 1) * this.pageSize;

    const params = new HttpParams()
      .set('limit', this.pageSize.toString())
      .set('offset', offset.toString())
      .set('timestamp', this.filters.timestamp)
      .set('total', this.filters.amount === 'min' ? 'asc' : 'desc')
      .set('tax', this.filters.tax === 'min' ? 'asc' : 'desc');

    this.http.get<any>(`https://le-silpo-production.up.railway.app/orders`, { params })
      .subscribe({
        next: (res) => {
          this.pagedOrders = res.data || [];
          this.totalItems = res.total || 0;
          this.cdr.detectChanges();
        }
      });
  }

  setFilter(category: keyof FilterState, value: string) {
    (this.filters as any)[category] = value;

    this.currentPage = 1;
    this.loadOrders();
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.loadOrders();
    }
  }

  get totalPages() {
    return Math.ceil(this.totalItems / this.pageSize) || 1;
  }

  get visiblePages(): number[] {
    const pages = [];
    let start = Math.max(1, this.currentPage - 2);
    let end = Math.min(this.totalPages, start + 4);
    for (let i = start; i <= end; i++) pages.push(i);
    return pages;
  }
}