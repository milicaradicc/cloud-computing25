import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OfflineReproductionComponent } from './offline-reproduction.component';

describe('OfflineReproductionComponent', () => {
  let component: OfflineReproductionComponent;
  let fixture: ComponentFixture<OfflineReproductionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [OfflineReproductionComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OfflineReproductionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
