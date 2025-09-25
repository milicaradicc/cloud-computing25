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

  getSong(songId: number): Observable<Song> {
    return this.httpClient.get<Song>(environment.apiHost + `/song/` + songId);
  }

  deleteAlbum(albumId: string): Observable<any> {
    return this.httpClient.delete(environment.apiHost + `/albums/${albumId}`);
  }

  deleteSong(song: Song): Observable<any> {
    console.log(song);
    const album = song.Album;
    const id = song.Id;
    console.log(album,id)
    return this.httpClient.delete(
      environment.apiHost + `/song?Album=${song.Album}&Id=${song.Id}`
    );
  }

  updateAlbum(albumId: string, album: Partial<Album>): Observable<any> {
    return this.httpClient.put(environment.apiHost + `/albums/${albumId}`, album);
  }

  updateSong(songId: string, song: Partial<Song>): Observable<any> {
    return this.httpClient.put(environment.apiHost + `/song/${songId}`, song);
  }
}