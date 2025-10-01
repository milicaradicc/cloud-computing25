import { Component, Input } from '@angular/core';
import { Song } from '../song.model';
import { environment } from '../../../env/environment';

@Component({
  selector: 'app-song-card',
  standalone: false,
  templateUrl: './song-card.component.html',
  styleUrls: ['./song-card.component.css']
})
export class SongCardComponent {
  @Input() song!: Song;

  getArtistNames(): string {
    return this.song.artists?.map(a => a.name).join(', ') || '';
  }

  getGenres(): string {
    return this.song.genres?.join(', ') || '';
  }

  getCoverUrl(): string {
    if (!this.song.coverImage) return "";
    console.log(environment.s3BucketLink + '/' + this.song.coverImage)
    return environment.s3BucketLink + '/' + this.song.coverImage;
  }

  onImageError(event: Event): void {
    const target = event.target as HTMLImageElement;
    target.style.display = 'none'; 
  }
}
