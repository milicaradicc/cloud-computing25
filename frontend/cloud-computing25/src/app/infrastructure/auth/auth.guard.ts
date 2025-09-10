import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, CanActivate, Router} from '@angular/router';
import {AuthService} from './auth.service';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  async canActivate(route: ActivatedRouteSnapshot): Promise<boolean> {
    await this.authService.loadRole();
    const userRole = this.authService.role$.getValue();

    if (!userRole) {
      this.router.navigate(['login']);
      return false;
    }

    if (route.data['role'] && !route.data['role'].includes(userRole)) {
      this.router.navigate(['home']);
      return false;
    }

    return true;
  }
}
