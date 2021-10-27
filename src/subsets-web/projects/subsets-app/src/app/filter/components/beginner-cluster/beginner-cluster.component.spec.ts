import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BeginnerClusterComponent } from './beginner-cluster.component';

describe('BeginnerClusterComponent', () => {
  let component: BeginnerClusterComponent;
  let fixture: ComponentFixture<BeginnerClusterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BeginnerClusterComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BeginnerClusterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
