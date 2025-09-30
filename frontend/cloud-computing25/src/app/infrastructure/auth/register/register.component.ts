import {Component, inject, OnInit} from '@angular/core';
import {AuthService} from '../auth.service';
import {AbstractControl, FormBuilder, FormGroup, ValidationErrors, Validators} from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import {Router} from '@angular/router';

@Component({
  selector: 'app-register',
  standalone: false,
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  registerForm: FormGroup;
  registerError: string | null = null;
  loading: boolean = false;
  snackBar: MatSnackBar = inject(MatSnackBar);

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router) {
    this.registerForm = this.fb.group({
      username: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required],
      givenName: ['', Validators.required],
      familyName: ['', Validators.required],
      birthdate: ['', Validators.required],
      isAdmin: [false, Validators.required],
    }, { validators: passwordMatchValidator });
  }

  async onSubmit() {
    this.registerError = null;
    this.loading = true;

    if (this.registerForm.valid) {
      const { username, email, password, givenName, familyName, birthdate, isAdmin } = this.registerForm.value;
      const role:string=isAdmin?'admin':'user';
      const user = { username, email, password, givenName, familyName, birthdate, role };
      try {
        await this.authService.register(user);
        this.snackBar.open('Registration successful!', 'OK', { duration: 3000 });
        this.router.navigate(['/home']);
      } catch (error: any) {
        this.registerError = error.message || 'An unexpected error occurred during registration.';
        console.error('Registration failed:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}


export const passwordMatchValidator = (control: AbstractControl): ValidationErrors | null => {
  const password = control.get('password');
  const confirmPassword = control.get('confirmPassword');
  return password && confirmPassword && password.value !== confirmPassword.value ? { 'mismatch': true } : null;
};
