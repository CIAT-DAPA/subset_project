import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BeginnerClusterMapComponent } from './beginner-cluster-map.component';

describe('BeginnerClusterMapComponent', () => {
  let component: BeginnerClusterMapComponent;
  let fixture: ComponentFixture<BeginnerClusterMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BeginnerClusterMapComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BeginnerClusterMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
