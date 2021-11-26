import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CandidateSubsetComponent } from './candidate-subset.component';

describe('CandidateSubsetComponent', () => {
  let component: CandidateSubsetComponent;
  let fixture: ComponentFixture<CandidateSubsetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CandidateSubsetComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CandidateSubsetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
