import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {HomeComponent} from './layout/home/home.component';
import {RegisterComponent} from './infrastructure/auth/register/register.component';
import {LoginComponent} from './infrastructure/auth/login/login.component';

const routes: Routes = [
  {path: 'home', component: HomeComponent},
  {path: '', redirectTo: '/home', pathMatch: 'full' },
  {path: 'register', component: RegisterComponent },
  {path: 'login', component: LoginComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
