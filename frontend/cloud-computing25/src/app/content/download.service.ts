import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../env/environment';

export interface DownloadResponse {
  url: string;
  filename: string;
}

@Injectable({
  providedIn: 'root'
})
export class DownloadService {
  constructor(private http: HttpClient) {}

  // API poziv koji vraća Observable
  downloadSong(songId: string): Observable<DownloadResponse> {
    return this.http.get<DownloadResponse>(`${environment.apiHost}/download/${songId}`);
  }

  initiateDownload(url: string, filename: string): void {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    link.click();
  }

  getPresignedUrl(songId: string): Observable<{ url: string; filename: string }> {
    return this.http.get<{ url: string; filename: string }>(
      `${environment.apiHost}/songs/${songId}/presigned-url`
    );
  }

}
