import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Song } from './song.model';
import { Album } from './album.model';
import { Artist } from '../artists/artist.model';

@Injectable({
  providedIn: 'root'
})
export class MusicService {
  constructor() {}

  uploadSong(song: FormData) {
    console.log('Uploading song:', song);
    // ovde ide HTTP POST ka backend-u
  }

  uploadAlbum(album: FormData) {
    console.log('Uploading album:', album);
    // ovde ide HTTP POST ka backend-u
  }
}