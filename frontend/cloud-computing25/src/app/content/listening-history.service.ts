import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../env/environment';

@Injectable({
  providedIn: 'root'
})
export class ListeningHistoryService {
  private apiUrl = `${environment.apiHost}/listening-history`;

  constructor(private http: HttpClient) { }

  recordListen(songId: string, album: string): Observable<any> {
    return this.http.post(this.apiUrl, { songId, album }).pipe(
        tap(() => console.log(`Listen event recorded for song: ${songId} from album: ${album}`))
    );
  }

  getHistory(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }
}