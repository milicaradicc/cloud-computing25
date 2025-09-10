import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {ArtistsComponent} from './artists/artists.component';
import {
  MatTableModule
} from '@angular/material/table';
import {MatIcon, MatIconModule} from '@angular/material/icon';
import {MatSortModule} from '@angular/material/sort';
import {MatButtonModule} from '@angular/material/button';
import {MatDialogModule} from '@angular/material/dialog';
import {MatSnackBarModule} from '@angular/material/snack-bar';


@NgModule({
  declarations: [
    ArtistsComponent
  ],
  imports: [
    CommonModule,
    MatTableModule,
    MatIconModule,
    MatSortModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatDialogModule,
    MatSnackBarModule,
    MatSortModule
  ]
})
export class ArtistsModule {
}
