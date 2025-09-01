import {Component, OnInit} from '@angular/core';
import {AuthService} from '../../infrastructure/auth/auth.service';

@Component({
  selector: 'app-nav-bar',
  standalone: false,
  templateUrl: './nav-bar.component.html',
  styleUrl: './nav-bar.component.css'
})
export class NavBarComponent implements OnInit{
  role: string | null='';

  constructor(private authService:AuthService) {
  }

  ngOnInit(): void {
    this.authService.roleState.subscribe(role => {
      this.role = role;
    });
  }

  logout(): void {
    this.authService.logout().then(() => {
      this.authService.loadRole();
    })
  }
}
