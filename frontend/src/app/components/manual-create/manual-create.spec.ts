import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManualCreate } from './manual-create';

describe('ManualCreate', () => {
  let component: ManualCreate;
  let fixture: ComponentFixture<ManualCreate>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManualCreate],
    }).compileComponents();

    fixture = TestBed.createComponent(ManualCreate);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
