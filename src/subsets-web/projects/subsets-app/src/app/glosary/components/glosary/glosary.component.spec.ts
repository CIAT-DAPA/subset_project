import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GlosaryComponent } from './glosary.component';

describe('GlosaryComponent', () => {
  let component: GlosaryComponent;
  let fixture: ComponentFixture<GlosaryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GlosaryComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GlosaryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
