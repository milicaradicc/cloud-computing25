import { Component, Input } from '@angular/core';
import { Song } from '../models/song.model';

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

  getCoverUrl(): string | null {
    if (!this.song.coverImage) return null;
    return typeof this.song.coverImage === 'string'
      ? this.song.coverImage
      : URL.createObjectURL(this.song.coverImage);
  }

  onImageError(event: Event): void {
    const target = event.target as HTMLImageElement;
    target.style.display = 'none'; // Sakrije sliku
    // Možeš dodati i fallback logiku, npr. da postaviš default sliku
    // target.src = 'assets/default-cover.png';
  }
}
