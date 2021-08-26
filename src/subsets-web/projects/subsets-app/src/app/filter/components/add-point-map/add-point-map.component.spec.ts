import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddPointMapComponent } from './add-point-map.component';

describe('AddPointMapComponent', () => {
  let component: AddPointMapComponent;
  let fixture: ComponentFixture<AddPointMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AddPointMapComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AddPointMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
