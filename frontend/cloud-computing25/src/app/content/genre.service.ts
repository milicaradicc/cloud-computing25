import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { environment } from '../../env/environment';
import { FilterResult } from './models/filtered-content.model';

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
    return this.httpClient.get<any>(url); 
  }
}