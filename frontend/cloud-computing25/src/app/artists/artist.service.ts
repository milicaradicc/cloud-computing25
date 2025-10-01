import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {Artist} from './artist.model';
import {environment} from '../../env/environment';
import {HttpClient} from '@angular/common/http';
import {CreateArtistDto} from './create-artist-dto.model';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ArtistService {

  constructor(private httpClient: HttpClient) { }

  get(id: string): Observable<Artist> {
    return this.httpClient.get<Artist>(`${environment.apiHost}/artists/${id}`);
  }

  getAll(): Observable<Artist[]> {
    return this.httpClient.get<Artist[]>(`${environment.apiHost}/artists`);
  }

  add(artist: CreateArtistDto): Observable<Artist> {
    return this.httpClient.post<Artist>(`${environment.apiHost}/artists`, artist);
  }

  update(id: string, artist: CreateArtistDto): Observable<Artist> {
    return this.httpClient.put<Artist>(`${environment.apiHost}/artists/${id}`, artist);
  }

  delete(artist: Artist): Observable<any> {
    return this.httpClient.delete(`${environment.apiHost}/artists?Genre=${artist.Genre}&Id=${artist.Id}`);
  }
}

