import {Component, inject} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {AuthService} from '../auth.service';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  loginForm: FormGroup;
  loginError: string | null = null;
  loading: boolean = false;
  snackBar: MatSnackBar = inject(MatSnackBar);

  constructor(private fb: FormBuilder, private authService: AuthService) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  async onSubmit() {
    this.loginError = null;
    this.loading = true;

    if (this.loginForm.valid) {
      const { username, password } = this.loginForm.value;
      try {
        await this.authService.login(username, password);
        this.snackBar.open('Login successful!', 'OK', { duration: 3000 });
      } catch (error: any) {
        this.loginError = error.message || 'An unexpected error occurred during login.';
        console.error('Login failed:', error);
      } finally {
        this.loading = false;
      }
    }
  }
}
