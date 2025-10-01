import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { ArtistService } from '../../artists/artist.service';
import { Artist } from '../../artists/artist.model';
import { SingleUploadDTO } from '../models/single-upload-dto.model';
import { ContentService } from '../content.service';
import { AlbumUploadDTO } from '../models/album-upload-dto.model';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  standalone: false,
  selector: 'app-upload-content',
  templateUrl: './upload-content.component.html',
  styleUrls: ['./upload-content.component.css']
})
export class UploadContentComponent implements OnInit {
  uploadForm: FormGroup;
  availableArtists: Artist[] = [];
  availableGenres: string[] = [
    'Pop', 'Rock', 'Hip Hop', 'Rap', 'Electronic',
    'Classical', 'Jazz', 'Blues', 'Country', 'Reggae'
  ];
  coverImagePreview: string | null = null;
  selectedAudioFileName: string = '';
  singleAudioInfo: any | null = null;
  coverFile: File | null = null;
  coverBase64: string | null = null;

  constructor(
    private fb: FormBuilder,
    private artistService: ArtistService,
    private musicService: ContentService,
    private snackBar: MatSnackBar
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

  // ----------- FormArray Getters -----------

  get songs(): FormArray {
    return this.uploadForm.get('songs') as FormArray;
  }

  addSongForm(): FormGroup {
    return this.fb.group({
      title: ['', Validators.required],
      artists: [[], Validators.required],
      genres: [[], Validators.required],
      audioFile: [null, Validators.required],
      audioInfo: [null],
      description: [''],
      coverImageUrl: ['']
    });
  }

  addSong(): void {
    this.songs.push(this.addSongForm());
  }

  removeSong(index: number): void {
    this.songs.removeAt(index);
  }

  // ----------- Load Artists -----------

  private loadArtists(): void {
    this.artistService.getAll().subscribe({
      next: artists => this.availableArtists = artists,
      error: err => console.error('Error loading artists:', err)
    });

    console.log('Available artists:', this.availableArtists);
  }

  // ----------- Cover Image Handling -----------

  onCoverFileChange(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    this.coverFile = file;
    const reader = new FileReader();
    reader.onload = (e: any) => {
      this.coverImagePreview = e.target.result; // za prikaz u UI
    };
    reader.readAsDataURL(file);

    this.uploadForm.patchValue({ coverImageUrl: file.name }); // ili možeš čuvati ime
  }

  onImageError() {
    this.coverImagePreview = null;
    console.warn('Failed to load image from the provided URL');
  }

  // ----------- Audio File Handling -----------

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

  onAlbumSongFileChange(event: any, index: number) {
    const file = event.target.files[0];
    if (!file) return;

    const audioInfo = this.extractFileInfo(file);
    const audio = new Audio();
    const objectUrl = URL.createObjectURL(file);
    audio.src = objectUrl;

    audio.addEventListener('loadedmetadata', () => {
      audioInfo.duration = Math.round(audio.duration);
      URL.revokeObjectURL(objectUrl);
      this.songs.at(index).patchValue({ audioInfo, audioFile: file });
    });

    audio.addEventListener('error', () => URL.revokeObjectURL(objectUrl));
  }

  private extractFileInfo(file: File): any {
    return {
      fileName: file.name,
      fileType: file.type,
      fileSize: file.size,
      createdDate: new Date(file.lastModified),
      modifiedDate: new Date(file.lastModified),
      duration: 0
    };
  }

  // ----------- Form Submission -----------

  async submit() {
    if (this.uploadForm.invalid) {
      console.error('Form invalid');
      return;
    }

    const formValue = this.uploadForm.value;

    if (formValue.type === 'single') {
      await this.uploadSingle(formValue);
    } else {
      await this.uploadAlbum(formValue);
    }

    this.snackBar.open('Your files are uploading!', 'OK', { duration: 3000 });
  }

  private async uploadSingle(formValue: any) {
    const file: File = formValue.singleFile;
    if (!file) return;

    const base64File = await this.convertFileToBase64(file);

    let coverBase64: string | null = null;
    if (this.coverFile) {
      coverBase64 = await this.convertFileToBase64(this.coverFile);
    }

    const albumDto: AlbumUploadDTO = {
      createdDate: new Date(),
      modifiedDate: new Date(),
      title: formValue.title,
      description: formValue.description,
      artists: formValue.artists,
      genres: formValue.genres,
      coverFileBase64: coverBase64 ?? undefined,
      coverFileName: this.coverFile?.name,
      single: true
    };

    console.log('Album DTO:', albumDto);

    this.musicService.addAlbum(albumDto).subscribe({
      next: albumRes => {
        const albumId = albumRes.item.Id;

        const dto: SingleUploadDTO = {
          fileBase64: base64File,
          fileName: crypto.randomUUID(),
          fileSize: file.size,
          fileType: file.type,
          createdDate: new Date(file.lastModified),
          modifiedDate: new Date(file.lastModified),
          duration: this.singleAudioInfo?.duration || 0,
          title: formValue.title,
          description: formValue.description,
          artists: formValue.artists,
          genres: formValue.genres,
          coverImage: this.coverFile?.name ?? "",
          album: albumId,
          single: true
        };

        console.log('Single DTO:', dto);

        this.musicService.addSong(dto).subscribe({
          next: res => console.log('Single uploaded successfully', res),
          error: err => console.error('Single upload failed', err)
        });
      },
      error: err => console.error('Album creation for single failed', err)
    });
  }

  private async uploadAlbum(formValue: any) {
    if (this.coverFile) {
      this.coverBase64 = await this.convertFileToBase64(this.coverFile);
    }

    const albumDto: AlbumUploadDTO = {
      createdDate: new Date(),
      modifiedDate: new Date(),
      title: formValue.title,
      description: formValue.description,
      artists: formValue.artists,
      genres: formValue.genres,
      coverFileBase64: this.coverBase64 ?? undefined,
      coverFileName: this.coverFile?.name,
      single: false
    };

    console.log('Album DTO:', albumDto);

    this.musicService.addAlbum(albumDto).subscribe({
      next: albumRes => {
        console.log('Album created:', albumRes);
        const albumId = albumRes.item.Id;

        this.songs.controls.forEach(async (songCtrl) => {
          const songControl = songCtrl as FormGroup;
          const songFile: File = songControl.value.audioFile;
          if (!songFile) return;

          const base64File = await this.convertFileToBase64(songFile);

          const songDto: SingleUploadDTO = {
            fileBase64: base64File,
            fileName: crypto.randomUUID(),
            fileSize: songFile.size,
            fileType: songFile.type,
            createdDate: new Date(songFile.lastModified),
            modifiedDate: new Date(songFile.lastModified),
            duration: songControl.value.audioInfo?.duration || 0,
            title: songControl.value.title,
            description: songControl.value.description,
            artists: songControl.value.artists,
            genres: songControl.value.genres,
            coverImage: songControl.value.coverImageUrl || formValue.coverImageUrl,
            album: albumId,
            single: false
          };

          console.log('Song DTO:', songDto);

          this.musicService.addSong(songDto).subscribe({
            next: res => console.log(`Song ${songDto.title} uploaded`, res),
            error: err => console.error(`Song ${songDto.title} upload failed`, err)
          });
        });
      },
      error: err => console.error('Album upload failed', err)
    });
  }

  // ----------- Helpers -----------

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
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
