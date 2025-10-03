import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

// Angular Material
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatRadioModule } from '@angular/material/radio';
import { MatCardActions, MatCardModule, MatCard } from '@angular/material/card';
import { MatDividerModule, MatDivider } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips'; 
import { MatDatepickerModule } from '@angular/material/datepicker'; 
import { MatNativeDateModule } from '@angular/material/core'; 
import { MatTableModule } from '@angular/material/table'; 
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; 
import { MatListModule, MatList } from '@angular/material/list'; 
import { MatDialogModule } from '@angular/material/dialog';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';

import { UploadContentComponent } from './upload-content/upload-content.component';
import { ContentComponent } from './content/content.component';
import { SongCardComponent } from './song-card/song-card.component';
import { AlbumCardComponent } from './album-card/album-card.component';
import { SongDetailsComponent } from './song-details/song-details.component';
import { ContentManagementComponent, ConfirmDeleteDialog } from './content-management/content-management.component';
import { UpdateAlbumComponent } from './update-album/update-album.component';
import { UpdateSongComponent } from './update-song/update-song.component';
import { DiscoverContentComponent } from './discover-content/discover-content.component';
import { AlbumDetailsComponent } from './album-details/album-details.component';
import { OfflineReproductionComponent } from './offline-reproduction/offline-reproduction.component';

@NgModule({
  declarations: [
    UploadContentComponent,
    ContentComponent,
    SongCardComponent,
    AlbumCardComponent,
    SongDetailsComponent,
    ContentManagementComponent,
    UpdateAlbumComponent,
    UpdateSongComponent,
    DiscoverContentComponent,
    AlbumDetailsComponent,
    OfflineReproductionComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    // Angular Material
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatRadioModule,
    MatChipsModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatTableModule,
    MatProgressSpinnerModule,
    MatDialogModule,
    MatTabsModule,
    MatTooltipModule,
    MatDialogModule,
    ConfirmDeleteDialog,
    MatCard,
    MatDivider,
    MatList,
    MatListModule,
    MatCardModule
],
  exports: [UploadContentComponent, AlbumCardComponent, SongCardComponent]
})
export class ContentModule { }