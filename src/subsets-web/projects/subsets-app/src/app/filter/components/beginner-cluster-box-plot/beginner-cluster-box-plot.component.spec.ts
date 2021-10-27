import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BeginnerClusterBoxPlotComponent } from './beginner-cluster-box-plot.component';

describe('BeginnerClusterBoxPlotComponent', () => {
  let component: BeginnerClusterBoxPlotComponent;
  let fixture: ComponentFixture<BeginnerClusterBoxPlotComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BeginnerClusterBoxPlotComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BeginnerClusterBoxPlotComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
