import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminNavBarMenuComponent } from './admin-nav-bar-menu.component';

describe('AdminNavBarMenuComponent', () => {
  let component: AdminNavBarMenuComponent;
  let fixture: ComponentFixture<AdminNavBarMenuComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AdminNavBarMenuComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminNavBarMenuComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
