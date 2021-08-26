import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AccessionsDetailComponent } from './accessions-detail.component';

describe('AccessionsDetailComponent', () => {
  let component: AccessionsDetailComponent;
  let fixture: ComponentFixture<AccessionsDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AccessionsDetailComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AccessionsDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
