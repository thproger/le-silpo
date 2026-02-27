import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Order } from '../model/order.model';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-orders-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './orders-list.html',
  styleUrls: ['./orders-list.css'],
})
export class OrdersList implements OnInit {
  orders: (Order & { isValid?: boolean })[] = [];
  currentPage = 1;


  constructor(private http: HttpClient) {}
  ngOnInit(): void {
    // Тут те саме
    this.http.get<Order[]>('http://localhost:8000/orders').subscribe(result => {
      console.log(result)
      this.orders = result
    })
  }
}
