import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {HomeComponent} from './layout/home/home.component';
import {RegisterComponent} from './infrastructure/auth/register/register.component';
import {LoginComponent} from './infrastructure/auth/login/login.component';
import {ArtistsComponent} from './artists/artists/artists.component';
import {AuthGuard} from './infrastructure/auth/auth.guard';
import { UploadContentComponent } from './content/upload-content/upload-content.component';
import { ContentComponent } from './content/content/content.component';

const routes: Routes = [
  {path: 'home', component: ContentComponent},
  {path: '', redirectTo: '/home', pathMatch: 'full'},
  {path: 'register', component: RegisterComponent},
  {path: 'login', component: LoginComponent},
  {path: 'artists', component: ArtistsComponent, canActivate: [AuthGuard],
    data: {role: ['admin']}},
  {path: 'upload', component: UploadContentComponent, canActivate: [AuthGuard],
    data: {role: ['admin']}},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
