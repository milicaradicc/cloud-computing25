import { Injectable } from '@angular/core';
import { signUp, signIn, signOut, fetchAuthSession, getCurrentUser, confirmSignUp } from 'aws-amplify/auth';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor() { }

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

  async getToken() {
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.toString();
  }
}
