import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlotOutcomesComponent } from './plot-outcomes.component';

describe('PlotOutcomesComponent', () => {
  let component: PlotOutcomesComponent;
  let fixture: ComponentFixture<PlotOutcomesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlotOutcomesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PlotOutcomesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
