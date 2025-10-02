// U src/app/services/feed.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../env/environment';
import { Song } from '../content/models/song.model';
import { Album } from '../content/models/album.model'

export interface FeedResponse {
  recommendedSongs: Song[];
  recommendedAlbums: Album[];
}

@Injectable({
  providedIn: 'root'
})
export class FeedService {

  constructor(private http: HttpClient) { }

  // === ISPRAVKA JE OVDE ===
  // Sada funkcija ispravno deklariše da vraća Observable<FeedResponse>
  getPersonalizedFeed(): Observable<FeedResponse> {
    // I http.get očekuje isti tip <FeedResponse>
    return this.http.get<FeedResponse>(`${environment.apiHost}/feed`);
  }
}