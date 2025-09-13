import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { ArtistService } from '../../artists/artist.service';
import { Artist } from '../../artists/artist.model';
import { SingleUploadDTO } from '../single-upload-dto.model';
import { ContentService } from '../content.service';
import { AlbumUploadDTO } from '../album-upload-dto.model';

@Component({
  standalone: false,
  selector: 'app-upload-content',
  templateUrl: './upload-content.component.html',
  styleUrls: ['./upload-content.component.css']
})
export class UploadContentComponent implements OnInit {
  uploadForm: FormGroup;
  availableArtists: Artist[] = [];
  availableGenres: string[] = ['Pop','Rock','Hip Hop','Rap','Electronic','Classical','Jazz','Blues','Country','Reggae'];
  selectedGenres: string[] = [];
  coverImagePreview: string | null = null;
  selectedAudioFileName: string = '';
  singleAudioInfo: any | null = null;

  constructor(
    private fb: FormBuilder,
    private artistService: ArtistService,
    private musicService: ContentService
  ) {
    this.uploadForm = this.fb.group({
      type: ['single', Validators.required],
      title: ['', Validators.required],
      coverImageUrl: [''],
      releaseDate: [new Date()],
      description: [''],
      artists: [[], Validators.required],
      genres: [[], Validators.required],
      singleFile: [null],
      songs: this.fb.array([])
    });
  }

  ngOnInit(): void {
    this.loadArtists();

    this.uploadForm.get('type')?.valueChanges.subscribe(type => {
      if (type === 'single') this.songs.clear();
    });
  }

  get songs(): FormArray {
    return this.uploadForm.get('songs') as FormArray;
  }

  private loadArtists(): void {
    this.artistService.getAll().subscribe({
      next: artists => this.availableArtists = artists,
      error: err => console.error('Error loading artists:', err)
    });
  }

  onCoverImageUrlChange(event: any) {
    const url = event.target.value;
    if (url) {
      this.coverImagePreview = url;
    } else {
      this.coverImagePreview = null;
    }
  }

  onImageError() {
    this.coverImagePreview = null;
    console.warn('Failed to load image from the provided URL');
  }

  onSingleAudioFileChange(event: any) {
    const file = event.target.files[0];
    if (!file) return;
    this.selectedAudioFileName = file.name;
    this.singleAudioInfo = this.extractFileInfo(file);
    this.uploadForm.patchValue({ singleFile: file });

    const audio = new Audio();
    const objectUrl = URL.createObjectURL(file);
    audio.src = objectUrl;

    audio.addEventListener('loadedmetadata', () => {
      if (this.singleAudioInfo) this.singleAudioInfo.duration = Math.round(audio.duration);
      URL.revokeObjectURL(objectUrl);
    });

    audio.addEventListener('error', () => URL.revokeObjectURL(objectUrl));
  }

  private extractFileInfo(file: File): any {
    return {
      fileName: file.name,
      fileType: file.type,
      fileSize: file.size,
      createdDate: new Date(file.lastModified),
      modifiedDate: new Date(file.lastModified)
    };
  }


  async submit() {
    if (this.uploadForm.invalid) {
      console.error('Form invalid');
      return;
    }

    const formValue = this.uploadForm.value;

    if (formValue.type === 'single') {
      const file: File = formValue.singleFile;
      if (!file) return;

      const base64File = await this.convertFileToBase64(file);

      const dto: SingleUploadDTO = {
        fileBase64: base64File,
        fileName: file.name,
        fileSize: file.size,
        fileType: file.type,
        createdDate: new Date(file.lastModified),
        modifiedDate: new Date(file.lastModified),
        duration: this.singleAudioInfo?.duration || 0,

        // this is from admin
        title: formValue.title,
        description: formValue.description,
        artists: formValue.artists.map((a: Artist) => a.id),
        genres: formValue.genres,
        coverImage: formValue.coverImageUrl,
        album: ''
      };

      this.musicService.addSong(dto).subscribe({
        next: res => console.log('Single uploaded successfully', res),
        error: err => console.error('Single upload failed', err)
      });

      return;
    }

    // ----- Album Upload -----
    const dto: AlbumUploadDTO = {
        createdDate: new Date(),
        modifiedDate: new Date(),
        title: formValue.title,
        description: formValue.description,
        artists: formValue.artists.map((a: Artist) => a.id),
        genres: formValue.genres,
        coverImage: formValue.coverImageUrl,
      };

      this.musicService.addAlbum(dto).subscribe({
        next: res => console.log('Album uploaded successfully', res),
        error: err => console.error('Album upload failed', err)
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
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes','KB','MB','GB'];
    const i = Math.floor(Math.log(bytes)/Math.log(k));
    return parseFloat((bytes/Math.pow(k,i)).toFixed(2)) + ' ' + sizes[i];
  }
}