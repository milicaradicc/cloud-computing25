import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { MatChipInputEvent } from '@angular/material/chips';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { Artist } from '../../artists/artist.model';
import { MusicService } from '../music.service';
import { Song } from '../song.model';
import { Album } from '../album.model';
import { ArtistService } from '../../artists/artist.service';

export interface FileInfo {
  fileName: string;
  fileType: string;
  fileSize: number;
  createdDate: Date;
  modifiedDate: Date;
  duration?: number;
}

@Component({
  standalone: false,
  selector: 'app-upload-content',
  templateUrl: './upload-content.component.html',
  styleUrls: ['./upload-content.component.css']
})
export class UploadContentComponent implements OnInit {
  uploadForm: FormGroup;
  availableArtists: Artist[] = [];
  selectedGenres: string[] = [];
  coverImagePreview: string | null = null;
  selectedCoverImageName: string = '';
  availableGenres: string[] = ['Pop', 'Rock', 'Hip Hop', 'Jazz', 'Electronic', 'Classical'];
  displayedColumns: string[] = ['trackNumber', 'title', 'file', 'genres', 'artists', 'duration', 'actions'];
  readonly separatorKeysCodes = [COMMA, ENTER] as const;

  constructor(private fb: FormBuilder, private musicService: MusicService,private artistService: ArtistService) {
    this.uploadForm = this.fb.group({
      type: ['single', Validators.required],
      title: ['', Validators.required],
      coverImage: [null],
      releaseDate: [new Date()],
      description: [''],
      artists: [[], Validators.required],
      songs: this.fb.array([])
    });
  }

  ngOnInit(): void {
    this.loadArtists();
    
    // Watch for type changes
    this.uploadForm.get('type')?.valueChanges.subscribe(type => {
      if (type === 'single') {
        // Clear songs array for single
        this.songs.clear();
      } else if (type === 'album' && this.songs.length === 0) {
        // Add initial song for album
        this.addSong();
      }
    });
  }

  get songs(): FormArray {
    return this.uploadForm.get('songs') as FormArray;
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
    // Update track numbers
    this.updateTrackNumbers();
  }

  private updateTrackNumbers() {
    this.songs.controls.forEach((control, index) => {
      control.patchValue({ trackNumber: index + 1 });
    });
  }

  onCoverImageChange(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    this.selectedCoverImageName = file.name;
    this.uploadForm.patchValue({ coverImage: file });

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      this.coverImagePreview = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }

  onSongFileChange(event: any, index: number) {
    const file = event.target.files[0];
    if (!file) return;

    const songGroup = this.songs.at(index);
    const fileInfo = this.extractFileInfo(file);
    
    songGroup.patchValue({ 
      file: file,
      fileName: file.name,
      fileInfo: fileInfo
    });

    // Extract audio duration
    this.extractAudioDuration(file, index);
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

  private extractAudioDuration(file: File, songIndex: number) {
    const audio = new Audio();
    const objectUrl = URL.createObjectURL(file);
    
    audio.src = objectUrl;
    audio.addEventListener('loadedmetadata', () => {
      const duration = Math.round(audio.duration);
      const songGroup = this.songs.at(songIndex);
      songGroup.patchValue({ duration: duration });
      
      // Update file info
      const currentFileInfo = songGroup.get('fileInfo')?.value;
      if (currentFileInfo) {
        currentFileInfo.duration = duration;
        songGroup.patchValue({ fileInfo: currentFileInfo });
      }
      
      URL.revokeObjectURL(objectUrl);
    });
    
    audio.addEventListener('error', () => {
      console.warn('Could not extract audio duration for file:', file.name);
      URL.revokeObjectURL(objectUrl);
    });
  }

  // Genre management for main form
  addGenre(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();
    
    if (value && !this.selectedGenres.includes(value)) {
      this.selectedGenres.push(value);
    }
    
    event.chipInput!.clear();
  }

  removeGenre(genre: string): void {
    const index = this.selectedGenres.indexOf(genre);
    if (index >= 0) {
      this.selectedGenres.splice(index, 1);
    }
  }

  // Genre management for individual songs
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

  submit() {
    if (this.uploadForm.invalid) {
      console.log('Form is invalid');
      return;
    }

    const formValue = this.uploadForm.value;
    const formData = new FormData();

    // Add cover image
    if (formValue.coverImage) {
      formData.append('coverImage', formValue.coverImage);
    }

    if (formValue.type === 'single') {
      // For single, we need to get file from first song or handle differently
      const singleData = {
        title: formValue.title,
        artists: formValue.artists,
        genres: this.selectedGenres,
        releaseDate: formValue.releaseDate,
        description: formValue.description
      };

      formData.append('songData', JSON.stringify(singleData));
      this.musicService.uploadSong(formData);
    } else {
      // For album
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

      // Add song files
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
      this.musicService.uploadAlbum(formData);
    }
  }

  private loadArtists(): void {
    // This would typically call a service
    // For now using empty array as in your original code
    this.artistService.getAll().subscribe(
      artists => this.availableArtists = artists,
      error => console.error('Error loading artists:', error)
    );
  }
}