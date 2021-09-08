import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FormSpecifcPerCropComponent } from './form-specifc-per-crop.component';

describe('FormSpecifcPerCropComponent', () => {
  let component: FormSpecifcPerCropComponent;
  let fixture: ComponentFixture<FormSpecifcPerCropComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FormSpecifcPerCropComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FormSpecifcPerCropComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
