import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ArtistService } from '../../artists/artist.service';
import { Artist } from '../../artists/artist.model';
import { Album } from '../models/album.model';
import { ContentService } from '../content.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { environment } from '../../../env/environment';

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

  selectedCoverFile: File | null = null;

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
        artists: selectedArtists.map(a => a.Id)
      });
    });
  }

  // ---------- COVER IMAGE ----------
  onCoverFileChange(event: any): void {
    const file = event.target.files[0];
    if (!file) return;

    this.selectedCoverFile = file;

    const reader = new FileReader();
    reader.onload = () => {
      this.form.patchValue({ coverImage: reader.result as string });
    };
    reader.readAsDataURL(file);
  }

  getCoverUrl(): string {
    const cover = this.form.value.coverImage;

    // Ako je uploadovana nova slika (base64)
    if (cover && cover.startsWith('data:image')) {
      return cover;
    }

    // Ako album već ima cover sa S3
    if (cover) {
      return environment.s3BucketLink + '/' + cover;
    }

    // Fallback
    return 'assets/placeholder.png';
  }

  // ---------- SAVE ----------
  async save(): Promise<void> {
    if (this.form.invalid) return;

    let coverBase64: string | undefined;
    if (this.selectedCoverFile) {
      coverBase64 = await this.convertFileToBase64(this.selectedCoverFile);
    }

    const formValue = this.form.value;

    const updatedAlbum: Album = {
      ...this.data.album,
      title: formValue.title,
      description: formValue.description,
      artists: formValue.artists,
      genres: formValue.genres,
      coverImage: this.selectedCoverFile
        ? crypto.randomUUID() 
        : formValue.coverImage,
      Id: this.data.album.Id
    };

    if (coverBase64) {
      (updatedAlbum as any).coverBase64 = coverBase64;
    }

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

  private convertFileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve((reader.result as string).split(',')[1]);
      reader.onerror = err => reject(err);
      reader.readAsDataURL(file);
    });
  }
}
