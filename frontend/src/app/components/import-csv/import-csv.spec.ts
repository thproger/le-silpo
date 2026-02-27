import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImportCsv } from './import-csv';

describe('ImportCsv', () => {
  let component: ImportCsv;
  let fixture: ComponentFixture<ImportCsv>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImportCsv],
    }).compileComponents();

    fixture = TestBed.createComponent(ImportCsv);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
