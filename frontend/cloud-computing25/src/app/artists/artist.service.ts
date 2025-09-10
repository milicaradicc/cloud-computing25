import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {Artist} from './artist.model';
import {environment} from '../../env/environment';
import {HttpClient} from '@angular/common/http';
import {CreateArtistDto} from './create-artist-dto.model';

@Injectable({
  providedIn: 'root'
})
export class ArtistService {

  constructor(private httpClient: HttpClient) { }

  getAll() : Observable<Artist[]> {
    return this.httpClient.get<Artist[]>(environment.apiHost + `/artists`);
  }

  add(artist:CreateArtistDto) : Observable<Artist> {
    return this.httpClient.post<Artist>(environment.apiHost + "/artists", artist);
  }
}
