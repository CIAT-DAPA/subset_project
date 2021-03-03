import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TableOutcomesComponent } from './table-outcomes.component';

describe('TableOutcomesComponent', () => {
  let component: TableOutcomesComponent;
  let fixture: ComponentFixture<TableOutcomesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TableOutcomesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TableOutcomesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
