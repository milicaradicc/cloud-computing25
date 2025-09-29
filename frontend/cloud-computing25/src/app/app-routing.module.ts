import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {HomeComponent} from './layout/home/home.component';
import {RegisterComponent} from './infrastructure/auth/register/register.component';
import {LoginComponent} from './infrastructure/auth/login/login.component';
import {ArtistsComponent} from './artists/artists/artists.component';
import {AuthGuard} from './infrastructure/auth/auth.guard';
import { UploadContentComponent } from './content/upload-content/upload-content.component';
import { ContentComponent } from './content/content/content.component';
import { DiscoverContentComponent } from './content/discover-content/discover-content.component';
import { ArtistPageComponent } from './artists/artist-page/artist-page.component';
import {SongDetailsComponent} from './content/song-details/song-details.component';
import { ContentManagementComponent } from './content/content-management/content-management.component';
import { SubscriptionsComponent } from './subscription/subscriptions/subscriptions.component';

const routes: Routes = [
  {path: 'home', component: ContentComponent},
  {path: 'subscriptions', component: SubscriptionsComponent, canActivate: [AuthGuard],
    data: {role: ['user']}},
  {path: '', redirectTo: '/home', pathMatch: 'full'},
  {path: 'register', component: RegisterComponent},
  {path: 'login', component: LoginComponent},
  {path: 'artists', component: ArtistsComponent, canActivate: [AuthGuard],
    data: {role: ['admin']}},
  {path: 'management', component: ContentManagementComponent, canActivate: [AuthGuard],
    data: {role: ['admin']}},
  {path: 'upload', component: UploadContentComponent, canActivate: [AuthGuard],
    data: {role: ['admin']}},
  {path: 'discover/filter', component: DiscoverContentComponent, canActivate: [AuthGuard],
  data: {role: ['user']}},
  { path: 'artist/:id', component: ArtistPageComponent }, 
  {path:'song-details/:id',component:SongDetailsComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
