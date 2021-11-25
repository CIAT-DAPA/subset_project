import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvancedClusterMapComponent } from './advanced-cluster-map.component';

describe('AdvancedClusterMapComponent', () => {
  let component: AdvancedClusterMapComponent;
  let fixture: ComponentFixture<AdvancedClusterMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdvancedClusterMapComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AdvancedClusterMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
