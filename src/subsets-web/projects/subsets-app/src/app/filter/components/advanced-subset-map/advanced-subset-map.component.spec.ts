import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvancedSubsetMapComponent } from './advanced-subset-map.component';

describe('AdvancedSubsetMapComponent', () => {
  let component: AdvancedSubsetMapComponent;
  let fixture: ComponentFixture<AdvancedSubsetMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdvancedSubsetMapComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AdvancedSubsetMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
