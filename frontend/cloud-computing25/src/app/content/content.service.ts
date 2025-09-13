import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Song } from './song.model';
import { Album } from './album.model';
import { environment } from '../../env/environment';
import { SingleUploadDTO } from './single-upload-dto.model';

@Injectable({
  providedIn: 'root'
})
export class ContentService {
  constructor(private httpClient: HttpClient) { }

  addSong(song: SingleUploadDTO): Observable<any> {
    console.log(song)
    return this.httpClient.post<Song>(
      environment.apiHost + `/song`,
      song
    );
  }

  addAlbum(album: FormData): Observable<Album> {
    
    // Debug FormData contents
    console.log("Album FormData contents:");
    album.forEach((value, key) => {
      if (value instanceof File) {
        console.log(`${key}: File - ${value.name} (${value.size} bytes)`);
      } else {
        console.log(`${key}:`, value);
      }
    });

    console.log(`API URL: ${environment.apiHost}/album`);
    
    return this.httpClient.post<Album>(
      environment.apiHost + `/album`,
      album
    );
  }

  getAllSongs(): Observable<Song[]> {
    return this.httpClient.get<Song[]>(environment.apiHost + `/song`);
  }

  getAllAlbums(): Observable<Album[]> {
    return this.httpClient.get<Album[]>(environment.apiHost + `/albums`);
  }
}