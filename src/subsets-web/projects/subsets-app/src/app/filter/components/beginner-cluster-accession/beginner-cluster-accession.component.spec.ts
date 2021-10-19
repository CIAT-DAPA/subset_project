import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BeginnerClusterAccessionComponent } from './beginner-cluster-accession.component';

describe('BeginnerClusterAccessionComponent', () => {
  let component: BeginnerClusterAccessionComponent;
  let fixture: ComponentFixture<BeginnerClusterAccessionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BeginnerClusterAccessionComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BeginnerClusterAccessionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
