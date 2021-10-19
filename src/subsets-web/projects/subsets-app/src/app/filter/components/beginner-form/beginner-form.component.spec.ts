import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BeginnerFormComponent } from './beginner-form.component';

describe('BeginnerFormComponent', () => {
  let component: BeginnerFormComponent;
  let fixture: ComponentFixture<BeginnerFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ BeginnerFormComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BeginnerFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
