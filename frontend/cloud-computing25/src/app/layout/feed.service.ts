// U src/app/services/feed.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../env/environment';
import { Song } from '../content/models/song.model';
import { Album } from '../content/models/album.model'

export interface FeedResponse {
  albums: Album[];
  songs: Song[];
  topArtist: TopArtist;
  topGenre: string | null;
}

export interface TopArtist {
  Content: string; // npr. "ARTIST#b003942a-62e7-42b6-9323-970f0676c7d2"
  Average: number;
}

export interface ScoreUpdateRequest {
  action: 'LISTEN' | 'RATE' | 'SUBSCRIBE';
  details: any;
}

@Injectable({
  providedIn: 'root'
})
export class FeedService {

  constructor(private http: HttpClient) { }

  getPersonalizedFeed(): Observable<FeedResponse> {
    return this.http.get<FeedResponse>(`${environment.apiHost}/feed`);
  }

  updateUserScore(action: 'LISTEN' | 'RATE' | 'SUBSCRIBE', details: any): Observable<any> {
    const payload: ScoreUpdateRequest = {
      action,
      details
    };

    return this.http.post(`${environment.apiHost}/feed`, payload);
  }

  pushNewContent(payload: { contentId: string, genres: string[], artists: string[] }) {
    return this.http.post(`${environment.apiHost}/feed/new-content`, payload);
  }

}