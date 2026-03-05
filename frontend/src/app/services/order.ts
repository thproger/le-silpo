import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Order } from '../model/order.model';

@Injectable({
  providedIn: 'root',
})
export class OrderService {
  private ordersSource = new BehaviorSubject<Order[]>([]);
  orders$ = this.ordersSource.asObservable();

  constructor() {}

  setOrders(orders: Order[]) {
    this.ordersSource.next(orders);
  }
}
