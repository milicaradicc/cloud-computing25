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
import { CreateArtistComponent } from './create-artist/create-artist.component';
import {MatFormField, MatInput, MatLabel} from '@angular/material/input';
import {ReactiveFormsModule} from '@angular/forms';
import { ArtistPageComponent } from './artist-page/artist-page.component';
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { ContentModule } from '../content/content.module';


@NgModule({
  declarations: [
    ArtistsComponent,
    CreateArtistComponent,
    ArtistPageComponent
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
    MatSortModule,
    MatFormField,
    MatLabel,
    MatFormField,
    MatInput,
    ReactiveFormsModule,
    MatFormField,
    MatProgressSpinnerModule,
    ContentModule
]
})
export class ArtistsModule {
}
