import { Injectable } from '@angular/core';
import {jwtDecode} from 'jwt-decode';
import { signUp, signIn, signOut, fetchAuthSession, getCurrentUser, confirmSignUp } from 'aws-amplify/auth';
import {BehaviorSubject, Observable} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private roleSubject = new BehaviorSubject<string | null>(null);
  role$: Observable<string | null> = this.roleSubject.asObservable();

  constructor() {
    this.loadRole();
  }

  async register(user: any) {
    return await signUp({
      username: user.username,
      password: user.password,
      options: {
        userAttributes: {
          email: user.email,
          birthdate: user.birthdate,
          given_name: user.givenName,
          family_name: user.familyName,
          'custom:role': user.role,
        },
      },
    });
  }

  async login(username: string, password: string) {
    return await signIn({ username: username, password });
  }

  async logout() {
    return await signOut();
  }

  async getUser() {
    const user = await getCurrentUser();
    return user;
  }

  public async loadRole() {
    try {
      const session = await fetchAuthSession();
      const idToken = session.tokens?.idToken?.toString();
      if (!idToken) {
        this.roleSubject.next(null);
        return;
      }

      const decoded: any = jwtDecode(idToken);
      const role = decoded['custom:role'] || null;
      this.roleSubject.next(role);
    } catch (err) {
      this.roleSubject.next(null);
    }
  }

  async getToken() {
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.toString();
  }
}
