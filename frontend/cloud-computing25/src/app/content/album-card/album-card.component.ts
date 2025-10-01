import { Component, Input } from '@angular/core';
import { Album } from '../album.model';
import { Song } from '../song.model';
import { environment } from '../../../env/environment';

@Component({
  selector: 'app-album-card',
  standalone: false,
  templateUrl: './album-card.component.html',
  styleUrls: ['./album-card.component.css']
})
export class AlbumCardComponent {
  @Input() album!: Album;
  @Input() songs: Song[] = [];

  getArtistNames(): string {
    return this.album.artists?.map(a => a.name).join(', ') || '';
  }

  getGenres(): string {
    return this.album.genres?.join(', ') || '';
  }

  formatDuration(seconds: number): string {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  getAlbumCoverUrl(): string {
    if (!this.album.coverImage) return '';
    console.log(environment.s3BucketLink + '/' + this.album.coverImage);
    return environment.s3BucketLink + '/' + this.album.coverImage;
  }

  onCoverError() {
    this.album.coverImage = '';
  }

  playAlbum() {
    console.log('Playing album:', this.album.title);
  }
}
