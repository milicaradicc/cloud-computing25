import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {ReactiveFormsModule} from '@angular/forms';
import {RegisterComponent} from './register/register.component';
import {MatFormField, MatInputModule} from '@angular/material/input';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatCardModule} from '@angular/material/card';
import {MatButton} from '@angular/material/button';



@NgModule({
  declarations: [
    RegisterComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormField,
    MatFormFieldModule,
    MatInputModule,
    MatCardModule,
    MatButton
  ]
})
export class AuthModule { }
