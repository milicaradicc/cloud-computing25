import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ArtistService } from '../../artists/artist.service';
import { Artist } from '../../artists/artist.model';
import { Album } from '../models/album.model';
import { ContentService } from '../content.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-update-album',
  standalone: false,
  templateUrl: './update-album.component.html',
  styleUrls: ['./update-album.component.css']
})
export class UpdateAlbumComponent implements OnInit {
  form: FormGroup;

  allArtists: Artist[] = [];
  allGenres: string[] = ['Pop', 'Rock', 'Jazz', 'Hip Hop', 'Classical'];

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<UpdateAlbumComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { album: Album },
    private artistService: ArtistService,
    private contentService: ContentService,
    private snackBar: MatSnackBar
  ) {
    this.form = this.fb.group({
      title: [data.album.title, Validators.required],
      description: [data.album.description],
      coverImage: [data.album.coverImage],
      artists: [data.album.artists?.map(a => a.Id) || [], Validators.required],
      genres: [data.album.genres || []]
    });
  }

  ngOnInit(): void {
    this.artistService.getAll().subscribe(artists => {
      this.allArtists = artists;
      const selectedArtists = this.data.album.artists || [];
      this.form.patchValue({
        artists: selectedArtists
      });
    });
  }

  save(): void {
    if (this.form.valid) {
      const formValue = this.form.value;
      
      const updatedAlbum: Album = {
        ...this.data.album, 
        title: formValue.title,
        description: formValue.description,
        coverImage: formValue.coverImage,
        artists: formValue.artists, 
        genres: formValue.genres,
        Id: this.data.album.Id 
      };

      console.log('Updating album:', updatedAlbum);

      this.contentService.updateAlbum(updatedAlbum).subscribe({
        next: (response) => {
          console.log('Album updated successfully:', response);
          this.dialogRef.close(true);
        },
        error: (error) => {
          console.error('Error updating album:', error);
          this.snackBar.open('Error updating album', 'Close', { duration: 3000 });
        }
      });
    }
  }
}
