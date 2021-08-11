import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MultivariableAnalysisComponent } from './multivariable-analysis.component';

describe('MultivariableAnalysisComponent', () => {
  let component: MultivariableAnalysisComponent;
  let fixture: ComponentFixture<MultivariableAnalysisComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MultivariableAnalysisComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MultivariableAnalysisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
