import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Song } from './song.model';
import { Album } from './album.model';
import { environment } from '../../env/environment';
import { SingleUploadDTO } from './single-upload-dto.model';
import { AlbumUploadDTO } from './album-upload-dto.model';
import { Rating } from './rating.model';

@Injectable({
  providedIn: 'root'
})
export class ContentService {
  constructor(private httpClient: HttpClient) { }

  addSong(song: SingleUploadDTO): Observable<any> {
    return this.httpClient.post<Song>(environment.apiHost + `/songs`, song
    );
  }

  addAlbum(album: AlbumUploadDTO): Observable<any> {
    return this.httpClient.post<Album>(environment.apiHost + `/albums`,album);
  }

  getAllSongs(): Observable<Song[]> {
    return this.httpClient.get<Song[]>(environment.apiHost + `/songs`);
  }

  getAllAlbums(): Observable<Album[]> {
    return this.httpClient.get<Album[]>(environment.apiHost + `/albums`);
  }

  getSong(songId: string): Observable<Song> {
    return this.httpClient.get<Song>(environment.apiHost + `/songs/` + songId);
  }

  deleteAlbum(album: Album): Observable<any> {
    return this.httpClient.delete(environment.apiHost + `/albums/${album.Id}`);
  }

  deleteSong(songId: string): Observable<any> {
    return this.httpClient.delete(environment.apiHost + `/songs/` + songId);
  }

  updateAlbum(album: Album): Observable<any> {
    return this.httpClient.put(environment.apiHost + `/albums/${album.Id}`, album);
  }

  updateSong(song: Song): Observable<any> {
    return this.httpClient.put(environment.apiHost + `/songs/${song.Id}`, song);
  }

  rateSong(rating: Rating): Observable<any> {
    return this.httpClient.post(environment.apiHost + `/songs/${rating.targetId}/rating`, rating);
  }

  getSongRating(songId:string,userId:string): Observable<Rating>{
    return this.httpClient.get<Rating>(environment.apiHost + `/songs/${songId}/rating?userId=${userId}`);
  }
}