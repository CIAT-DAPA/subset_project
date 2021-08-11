import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FormSubsetComponent } from './form-subset.component';

describe('FormSubsetComponent', () => {
  let component: FormSubsetComponent;
  let fixture: ComponentFixture<FormSubsetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FormSubsetComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FormSubsetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
