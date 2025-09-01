import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserNavBarMenuComponent } from './user-nav-bar-menu.component';

describe('UserNavBarMenuComponent', () => {
  let component: UserNavBarMenuComponent;
  let fixture: ComponentFixture<UserNavBarMenuComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [UserNavBarMenuComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserNavBarMenuComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
