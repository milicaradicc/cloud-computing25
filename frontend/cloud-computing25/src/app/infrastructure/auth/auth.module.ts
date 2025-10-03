import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {ReactiveFormsModule} from '@angular/forms';
import {RegisterComponent} from './register/register.component';
import {MatFormField, MatInputModule} from '@angular/material/input';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatCardModule} from '@angular/material/card';
import {MatButton} from '@angular/material/button';
import { LoginComponent } from './login/login.component';
import {RouterLink} from '@angular/router';
import {MatCheckbox} from "@angular/material/checkbox";



@NgModule({
  declarations: [
    RegisterComponent,
    LoginComponent
  ],
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatFormField,
        MatFormFieldModule,
        MatInputModule,
        MatCardModule,
        MatButton,
        RouterLink,
        MatCheckbox
    ]
})
export class AuthModule { }
