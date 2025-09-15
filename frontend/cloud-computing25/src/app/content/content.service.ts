import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Song } from './song.model';
import { Album } from './album.model';
import { environment } from '../../env/environment';
import { SingleUploadDTO } from './single-upload-dto.model';
import { AlbumUploadDTO } from './album-upload-dto.model';

@Injectable({
  providedIn: 'root'
})
export class ContentService {
  constructor(private httpClient: HttpClient) { }

  addSong(song: SingleUploadDTO): Observable<any> {
    return this.httpClient.post<Song>(
      environment.apiHost + `/song`,
      song
    );
  }

  addAlbum(album: AlbumUploadDTO): Observable<any> {
    return this.httpClient.post<Album>(
      environment.apiHost + `/albums`,
      album
    );
  }

  getAllSongs(): Observable<Song[]> {
    return this.httpClient.get<Song[]>(environment.apiHost + `/song`);
  }

  getAllAlbums(): Observable<Album[]> {
    return this.httpClient.get<Album[]>(environment.apiHost + `/albums`);
  }

  getSong(songId:number):Observable<Song> {
    return this.httpClient.get<Song>(environment.apiHost + `/song/`+songId);
  }
}
