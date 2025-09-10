import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {Artist} from './artist.model';
import {environment} from '../../env/environment';
import {HttpClient} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ArtistService {

  constructor(private httpClient: HttpClient) { }

  getAll() : Observable<Artist[]> {
    return this.httpClient.get<Artist[]>(environment.apiHost + `/artists`);
  }

}
