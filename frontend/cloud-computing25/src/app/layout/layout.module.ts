import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HomeComponent } from './home/home.component';
import { NavBarComponent } from './nav-bar/nav-bar.component';
import {RouterLink} from '@angular/router';
import {MatToolbar} from '@angular/material/toolbar';
import {MatIconButton} from '@angular/material/button';
import {MatMenu, MatMenuItem, MatMenuTrigger} from '@angular/material/menu';
import {MatIcon} from '@angular/material/icon';
import { AdminNavBarMenuComponent } from './admin-nav-bar-menu/admin-nav-bar-menu.component';
import { UserNavBarMenuComponent } from './user-nav-bar-menu/user-nav-bar-menu.component';
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { ContentModule } from "../content/content.module";
import { MatDivider } from "@angular/material/divider";
import { MatCardActions } from "@angular/material/card";



@NgModule({
  declarations: [
    HomeComponent,
    NavBarComponent,
    AdminNavBarMenuComponent,
    UserNavBarMenuComponent
  ],
  exports: [
    NavBarComponent
  ],
  imports: [
    CommonModule,
    RouterLink,
    MatToolbar,
    MatIcon,
    MatIconButton,
    MatMenuItem,
    MatMenu,
    MatMenuTrigger,
    MatProgressSpinnerModule,
    ContentModule,
    MatDivider,
    MatCardActions
]
})
export class LayoutModule { }
