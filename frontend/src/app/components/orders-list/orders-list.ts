import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Order } from '../../model/order.model';

@Component({
  selector: 'app-orders-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './orders-list.html',
  styleUrls: ['./orders-list.css']
})
export class OrdersList implements OnInit {
  orders: (Order & { isValid?: boolean })[] = [
    { id: 456743, longitude: 30.523, latitude: 50.450, timestamp: '2024-05-20 12:00', subtotal: 100, tax: 20, total: 120, isValid: true },
    { id: 456744, longitude: 30.524, latitude: 50.451, timestamp: '2024-05-20 12:05', subtotal: 200, tax: 40, total: 240, isValid: false },
    // Додай більше об'єктів для тестування
  ];

  currentPage = 1;

  ngOnInit(): void {
  }
}