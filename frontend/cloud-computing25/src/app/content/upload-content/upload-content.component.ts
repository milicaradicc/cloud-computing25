import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { MatChipInputEvent } from '@angular/material/chips';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { Artist } from '../../artists/artist.model';
import { ArtistService } from '../../artists/artist.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MusicService } from '../music.service';

export interface FileInfo {
  fileName: string;
  fileType: string;
  fileSize: number;
  createdDate: Date;
  modifiedDate: Date;
  duration?: number;
}

@Component({
  selector: 'app-upload-content',
  standalone: false,
  templateUrl: './upload-content.component.html',
  styleUrls: ['./upload-content.component.css']
})
export class UploadContentComponent implements OnInit {

  uploadForm: FormGroup;
  availableArtists: Artist[] = [];
  selectedGenres: string[] = [];
  coverImagePreview: string | null = null;
  selectedCoverImageName: string = '';
  availableGenres: string[] = ['Pop','Rock','Hip Hop','Rap','Electronic','Classical','Jazz','Blues','Country','Reggae','Folk','Metal','Punk','Soul','Funk','Disco','Techno','Indie','Alternative','R&B','Gospel','Ska','Reggaeton','Salsa','Bachata','Merengue','Cumbia','Flamenco','Bolero','Tango','Cha Cha','Samba','Bossa Nova','Bulldog','Zouk','Afrobeat','Ballet','Conjunto','Cantopop','Chant','Choral','Crossover','Dance','Dangdut','Downtempo','Dub','Dubstep','EDM','Electro','Emo','Fado','Filmi','Folklore','Funk','Garage','Glam','Gospel','Grindcore','Grunge','Hardcore','Hardstyle','Hipster','House','Jungle','Klezmer','Lounge','Mambo','Mellow','Minimal','Moombahton','New Age','New Wave','Nu Jazz','Opera','Orchestral','Post','Power','Progressive','Psychedelic','Ragtime','Riddim','Rock','Sarabande','Singer','Singer-songwriter','Slow','Smooth','Son','Soul','Space','Speed','Swing','Symphonic','Synth','Techno','Three','Two','Vocal','Waltz','Zap','Zydeco'];
  displayedColumns: string[] = ['trackNumber', 'title', 'file', 'genres', 'artists', 'duration', 'actions'];
  readonly separatorKeysCodes = [COMMA, ENTER] as const;

  selectedAudioFileName: string = '';
  singleAudioInfo: FileInfo | null = null;

  constructor(
    private fb: FormBuilder,
    private artistService: ArtistService,
    private http: HttpClient,
    private musicService: MusicService
  ) {
    this.uploadForm = this.fb.group({
    type: ['single', Validators.required],
    title: ['', Validators.required],
    coverImage: [null],
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
      if (type === 'single') {
        this.songs.clear();
      } else if (type === 'album' && this.songs.length === 0) {
        this.addSong();
      }
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

  onCoverImageChange(event: any) {
    const file = event.target.files[0];
    if (!file) return;
    this.selectedCoverImageName = file.name;
    this.uploadForm.patchValue({ coverImage: file });
    const reader = new FileReader();
    reader.onload = e => this.coverImagePreview = e.target?.result as string;
    reader.readAsDataURL(file);
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

    audio.addEventListener('error', () => {
      console.warn('Could not extract audio duration for file:', file.name);
      URL.revokeObjectURL(objectUrl);
    });
  }

  private extractFileInfo(file: File): FileInfo {
    return {
      fileName: file.name,
      fileType: file.type,
      fileSize: file.size,
      createdDate: new Date(file.lastModified),
      modifiedDate: new Date(file.lastModified)
    };
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  formatDuration(seconds: number): string {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  addSong() {
    const songGroup = this.fb.group({
      title: ['', Validators.required],
      file: [null, Validators.required],
      fileName: [''],
      fileInfo: [null],
      genres: [[]],
      artists: [[], Validators.required],
      duration: [null],
      trackNumber: [this.songs.length + 1]
    });
    this.songs.push(songGroup);
  }

  removeSong(index: number) {
    this.songs.removeAt(index);
    this.updateTrackNumbers();
  }

  private updateTrackNumbers() {
    this.songs.controls.forEach((control, index) => {
      control.patchValue({ trackNumber: index + 1 });
    });
  }

  onSongFileChange(event: any, index: number) {
    const file = event.target.files[0];
    if (!file) return;
    const songGroup = this.songs.at(index);
    const fileInfo = this.extractFileInfo(file);
    songGroup.patchValue({ file, fileName: file.name, fileInfo });

    const audio = new Audio();
    const objectUrl = URL.createObjectURL(file);
    audio.src = objectUrl;

    audio.addEventListener('loadedmetadata', () => {
      songGroup.patchValue({ duration: Math.round(audio.duration) });
      fileInfo.duration = Math.round(audio.duration);
      songGroup.patchValue({ fileInfo });
      URL.revokeObjectURL(objectUrl);
    });

    audio.addEventListener('error', () => URL.revokeObjectURL(objectUrl));
  }

  addGenre(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    if (value && !this.selectedGenres.includes(value)) this.selectedGenres.push(value);
    event.chipInput!.clear();
  }

  removeGenre(genre: string): void {
    const index = this.selectedGenres.indexOf(genre);
    if (index >= 0) this.selectedGenres.splice(index, 1);
  }

  addSongGenre(event: MatChipInputEvent, songIndex: number): void {
    const value = (event.value || '').trim();
    const songGroup = this.songs.at(songIndex);
    const currentGenres = songGroup.get('genres')?.value || [];
    if (value && !currentGenres.includes(value)) {
      currentGenres.push(value);
      songGroup.patchValue({ genres: currentGenres });
    }
    event.chipInput!.clear();
  }

  removeSongGenre(genre: string, songIndex: number): void {
    const songGroup = this.songs.at(songIndex);
    const currentGenres = songGroup.get('genres')?.value || [];
    const index = currentGenres.indexOf(genre);
    if (index >= 0) {
      currentGenres.splice(index, 1);
      songGroup.patchValue({ genres: currentGenres });
    }
  }

  getSongGenres(songIndex: number): string[] {
    return this.songs.at(songIndex).get('genres')?.value || [];
  }

  submit() {
  console.log('Submit clicked!');
  if (this.uploadForm.invalid) {
    console.error('Form is invalid');
    return;
  }

  const formValue = this.uploadForm.value;

  // ----- Single Upload -----
  if (formValue.type === 'single') {
    const file: File = formValue.singleFile;
    if (!file) {
      console.error('No audio file selected');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', formValue.title);
    formData.append('releaseDate', formValue.releaseDate.toISOString());
    formData.append('description', formValue.description || '');
    formData.append('artists', JSON.stringify(formValue.artists));
    formData.append('genres', JSON.stringify(this.selectedGenres));
    if (this.singleAudioInfo) formData.append('fileInfo', JSON.stringify(this.singleAudioInfo));

    this.musicService.addSong(formData).subscribe({
      next: res => console.log('Single uploaded successfully', res),
      error: err => console.error('Single upload failed', err)
    });

    return;
  }

  // ----- Album Upload -----
  const albumData = {
    title: formValue.title,
    artists: formValue.artists,
    genres: this.selectedGenres,
    releaseDate: formValue.releaseDate,
    description: formValue.description,
    songs: formValue.songs.map((song: any, index: number) => ({
      ...song,
      trackNumber: index + 1
    }))
  };

  const formData = new FormData();
  if (formValue.coverImage) formData.append('coverImage', formValue.coverImage);
  formValue.songs.forEach((song: any, index: number) => {
    if (song.file) {
      formData.append(`songFile_${index}`, song.file);
      formData.append(`songMetadata_${index}`, JSON.stringify({
        title: song.title,
        artists: song.artists,
        genres: song.genres,
        trackNumber: song.trackNumber,
        fileInfo: song.fileInfo
      }));
    }
  });
  formData.append('albumData', JSON.stringify(albumData));

  this.musicService.addAlbum(formData).subscribe({
    next: res => console.log('Album uploaded successfully', res),
    error: err => console.error('Album upload failed', err)
  });
  }
}
