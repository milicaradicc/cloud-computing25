import { Component, Input } from '@angular/core';
import { environment } from '../../../env/environment';
import { Album } from '../models/album.model';
import { Song } from '../models/song.model';

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
    if (this.album.artists && this.album.artists.length > 0) {
      return this.album.artists.map(a => a.name).join(', ');
    }

    if (this.songs && this.songs.length > 0) {
      const artistNames = this.songs
        .flatMap(song => song.artists?.map(a => a.name) || [])
        .filter((v, i, a) => a.indexOf(v) === i); 
      return artistNames.join(', ');
    }

    return '';
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
    console.log(this.album.coverImage);
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
