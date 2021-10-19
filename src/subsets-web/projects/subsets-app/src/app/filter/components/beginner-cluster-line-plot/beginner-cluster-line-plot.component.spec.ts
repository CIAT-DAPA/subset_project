import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BeginnerClusterLinePlotComponent } from './beginner-cluster-line-plot.component';

describe('BeginnerClusterLinePlotComponent', () => {
  let component: BeginnerClusterLinePlotComponent;
  let fixture: ComponentFixture<BeginnerClusterLinePlotComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BeginnerClusterLinePlotComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BeginnerClusterLinePlotComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
