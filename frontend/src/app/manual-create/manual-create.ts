import { Component } from '@angular/core';
import { FormArray, FormBuilder, FormGroup } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-manual-create',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './manual-create.html',
  styleUrl: './manual-create.css',
})
export class ManualCreate {
  orderForm: FormGroup;

  constructor(private fb: FormBuilder) {
    this.orderForm = this.fb.group({
      rows: this.fb.array([this.createRow()]),
    });
  }

  get rows() {
    return this.orderForm.get('rows') as FormArray;
  }

  createRow() {
    return this.fb.group({
      id: [''],
      longitude: [''],
      latitude: [''],
      timestamp: [''],
      subtotal: [''],
      tax: [''],
      total: [''],
    });
  }

  addRow() {
    this.rows.push(this.createRow());
    
  }
}
