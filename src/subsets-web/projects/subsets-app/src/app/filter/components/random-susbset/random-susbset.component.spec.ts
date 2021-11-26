import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RandomSusbsetComponent } from './random-susbset.component';

describe('RandomSusbsetComponent', () => {
  let component: RandomSusbsetComponent;
  let fixture: ComponentFixture<RandomSusbsetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RandomSusbsetComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RandomSusbsetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
