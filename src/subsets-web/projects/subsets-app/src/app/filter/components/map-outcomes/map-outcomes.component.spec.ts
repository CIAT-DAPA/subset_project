import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MapOutcomesComponent } from './map-outcomes.component';

describe('MapOutcomesComponent', () => {
  let component: MapOutcomesComponent;
  let fixture: ComponentFixture<MapOutcomesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MapOutcomesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MapOutcomesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
