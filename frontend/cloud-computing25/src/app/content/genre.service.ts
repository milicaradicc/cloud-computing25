import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Song } from './song.model';
import { Album } from './album.model';
import { environment } from '../../env/environment';
import { SingleUploadDTO } from './single-upload-dto.model';
import { AlbumUploadDTO } from './album-upload-dto.model';
import { FilterResult } from './filtered-content.model';

@Injectable({
  providedIn: 'root'
})
export class GenreService {
  constructor(private httpClient: HttpClient) { }

  getAllGenres(): Observable<string[]> {
    return this.httpClient.get<string[]>(environment.apiHost + `/genres`);
  }

  getFilteredContent(genre: string): Observable<FilterResult> {
    const url = `${environment.apiHost}/discover/filter?genre=${encodeURIComponent(genre)}`;
    return this.httpClient.get<FilterResult>(url); 
  }
}