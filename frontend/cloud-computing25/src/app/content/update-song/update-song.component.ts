import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ArtistService } from '../../artists/artist.service';
import { Artist } from '../../artists/artist.model';
import { ContentService } from '../content.service';
import { SingleUploadDTO } from '../single-upload-dto.model';
import { Song } from '../song.model';

@Component({
  selector: 'app-update-song',
  standalone: false,
  templateUrl: './update-song.component.html',
  styleUrls: ['./update-song.component.css']
})
export class UpdateSongComponent implements OnInit {
  form: FormGroup;

  selectedFile: File | null = null;
  audioInfo: any = null;

  allArtists: Artist[] = [];
  allGenres: string[] = ['Pop', 'Rock', 'Jazz', 'Hip Hop', 'Classical'];

  constructor(
    private fb: FormBuilder,
    private artistService: ArtistService,
    private contentService: ContentService,
    private dialogRef: MatDialogRef<UpdateSongComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { song: Song }
  ) {
    this.form = this.fb.group({
      title: [data.song.title, Validators.required],
      description: [data.song.description],
      coverImage: [data.song.coverImage],
      artists: [data.song.artists?.map(a => a.Id) || [], Validators.required],
      genres: [data.song.genres || []]
    });

    this.audioInfo = {
      fileName: data.song.fileName,
      fileType: data.song.fileType,
      fileSize: data.song.fileSize,
      duration: data.song.duration
    };
  }

  ngOnInit(): void {
    this.artistService.getAll().subscribe(artists => {
      this.allArtists = artists;
      const selectedArtists = this.data.song.artists || [];
      this.form.patchValue({
        artists: selectedArtists
      });
    });
  }

  onFileChange(event: any): void {
    const file = event.target.files[0];
    if (!file) return;

    this.selectedFile = file;
    const audio = new Audio();
    const objectUrl = URL.createObjectURL(file);
    audio.src = objectUrl;

    audio.addEventListener('loadedmetadata', () => {
      this.audioInfo = {
        fileName: crypto.randomUUID(),
        fileType: file.type,
        fileSize: file.size,
        duration: Math.round(audio.duration)
      };
      URL.revokeObjectURL(objectUrl);
    });

    audio.addEventListener('error', () => URL.revokeObjectURL(objectUrl));
  }

  async save(): Promise<void> {
    if (this.form.invalid) return;

    let fileBase64: string | undefined;
    if (this.selectedFile) {
      fileBase64 = await this.convertFileToBase64(this.selectedFile);
    }

    const updatedSong: any = {
      ...this.data.song,
      ...this.form.value,
      modifiedDate: new Date(),
      duration: this.audioInfo?.duration || this.data.song.duration
    };

    if (fileBase64) {
      updatedSong.fileBase64 = fileBase64;
      updatedSong.fileName = crypto.randomUUID();
      updatedSong.fileType = this.selectedFile!.type;
      updatedSong.fileSize = this.selectedFile!.size;
    }

    this.contentService.updateSong(updatedSong).subscribe({
      next: () => this.dialogRef.close(true),
      error: (err) => console.error('Update song failed', err)
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

  formatDuration(seconds: number): string {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2,'0')}`;
  }

  formatFileSize(bytes: number): string {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes','KB','MB','GB'];
    const i = Math.floor(Math.log(bytes)/Math.log(k));
    return parseFloat((bytes/Math.pow(k,i)).toFixed(2)) + ' ' + sizes[i];
  }
}
