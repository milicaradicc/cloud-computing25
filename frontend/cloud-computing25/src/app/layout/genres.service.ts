import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable, of } from 'rxjs';
import { environment } from '../../env/environment';
import { FilterResult } from '../content/filter-result.model';

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
    return this.httpClient.get<any>(url).pipe(
      map(response => ({
        artists: response.artists?.Items || [],
        albums: response.albums?.Items || []
      }))
    );
  }
}