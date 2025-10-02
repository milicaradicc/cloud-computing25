import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DiscoverContentComponent } from './discover-content.component';

describe('DiscoverContentComponent', () => {
  let component: DiscoverContentComponent;
  let fixture: ComponentFixture<DiscoverContentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DiscoverContentComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DiscoverContentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
