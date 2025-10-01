import { Component, Inject } from '@angular/core';
import { Album } from '../album.model';
import { Song } from '../song.model';
import { ContentService } from '../content.service';
import { MAT_DIALOG_DATA, MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatButtonModule } from '@angular/material/button';
import { UpdateAlbumComponent } from '../update-album/update-album.component';
import { UpdateSongComponent } from '../update-song/update-song.component';
import { environment } from '../../../env/environment';

@Component({
  selector: 'app-content-management',
  standalone: false,
  templateUrl: './content-management.component.html',
  styleUrl: './content-management.component.css'
})
export class ContentManagementComponent {
albums: Album[] = [];
  songs: Song[] = [];
  filteredAlbums: Album[] = [];
  filteredSongs: Song[] = [];
  albumSearchTerm: string = '';
  songSearchTerm: string = '';
  loading = false;

  constructor(
    private contentService: ContentService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  getAlbumCoverUrl(album: Album): string {
    if (!album.coverImage) return "assets/placeholder.png";
    console.log( environment.s3BucketLink + '/' + album.coverImage)
    return environment.s3BucketLink + '/' + album.coverImage;
  }

  getSongCoverUrl(song: Song): string {
    if (!song.coverImage) return "assets/default-song.png";
    console.log( environment.s3BucketLink + '/' + song.coverImage)
    return environment.s3BucketLink + '/' + song.coverImage;
  }

  loadData(): void {
    this.loading = true;
    
    // Load albums
    this.contentService.getAllAlbums().subscribe({
      next: (albums) => {
        this.albums = albums;
        this.filteredAlbums = [...albums];
      },
      error: (error) => {
        console.error('Error loading albums:', error);
        this.showMessage('Error loading albums');
      }
    });

    // Load songs
    this.contentService.getAllSongs().subscribe({
      next: (songs) => {
        this.songs = songs;
        this.filteredSongs = [...songs];
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading songs:', error);
        this.showMessage('Error loading songs');
        this.loading = false;
      }
    });
  }

  filterAlbums(): void {
    if (!this.albumSearchTerm.trim()) {
      this.filteredAlbums = [...this.albums];
      return;
    }

    const searchTerm = this.albumSearchTerm.toLowerCase();
    this.filteredAlbums = this.albums.filter(album =>
      album.title.toLowerCase().includes(searchTerm) ||
      album.artists.some(artist => artist.name.toLowerCase().includes(searchTerm)) ||
      album.genres?.some(genre => genre.toLowerCase().includes(searchTerm))
    );
  }

  filterSongs(): void {
    if (!this.songSearchTerm.trim()) {
      this.filteredSongs = [...this.songs];
      return;
    }

    const searchTerm = this.songSearchTerm.toLowerCase();
    this.filteredSongs = this.songs.filter(song =>
      song.title.toLowerCase().includes(searchTerm) ||
      song.artists.some(artist => artist.name.toLowerCase().includes(searchTerm)) ||
      song.Album?.toLowerCase().includes(searchTerm) ||
      song.genres?.some(genre => genre.toLowerCase().includes(searchTerm))
    );
  }

  deleteAlbum(album: Album): void {
    const dialogRef = this.dialog.open(ConfirmDeleteDialog, {
      data: { 
        title: 'Delete Album', 
        message: `Are you sure you want to delete the album "${album.title}"? This action cannot be undone.` 
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        album.deleted = true;
        
        this.contentService.deleteAlbum(album).subscribe({
          next: () => {
            this.showMessage('Album deleted successfully');
            this.loadData(); 
          },
          error: (error) => {
            console.error('Error deleting album:', error);
            this.showMessage('Error deleting album');
            album.deleted = false;
          }
        });
      }
    });
  }

  deleteSong(song: Song): void {
    const dialogRef = this.dialog.open(ConfirmDeleteDialog, {
      data: { 
        title: 'Delete Song', 
        message: `Are you sure you want to delete the song "${song.title}"? This action cannot be undone.` 
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        song.deleted = true;
        
        this.contentService.deleteSong(song.Id).subscribe({
          next: () => {
            this.showMessage('Song deleted successfully');
            this.loadData(); 
          },
          error: (error) => {
            console.error('Error deleting song:', error);
            this.showMessage('Error deleting song');
            song.deleted = false;
          }
        });
      }
    });
  }


  viewAlbumDetails(album: Album): void {
    console.log('View album details:', album);
  }

  editAlbum(album: Album): void {
    const dialogRef = this.dialog.open(UpdateAlbumComponent, {
      width: '600px',
      data: { album }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showMessage('Album updated successfully');
        this.loadData();
      }
    });
  }


  editSong(song: Song): void {
    const dialogRef = this.dialog.open(UpdateSongComponent, {
      width: '600px',
      data: { song }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.showMessage('Song updated successfully');
        this.loadData();
      }
    });
  }

  formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  private showMessage(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'end',
      verticalPosition: 'bottom'
    });
  }
}

@Component({
  selector: 'confirm-delete-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule],
  template: `
    <h1 mat-dialog-title>{{data.title}}</h1>
    <div mat-dialog-content>
      <p>{{data.message}}</p>
    </div>
    <div mat-dialog-actions>
      <button mat-button [mat-dialog-close]="false">Cancel</button>
      <button mat-button color="warn" [mat-dialog-close]="true">Delete</button>
    </div>
  `
})
export class ConfirmDeleteDialog {
  constructor(@Inject(MAT_DIALOG_DATA) public data: any) {}
}