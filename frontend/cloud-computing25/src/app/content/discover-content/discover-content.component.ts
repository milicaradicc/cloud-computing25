import { Component, OnInit } from '@angular/core';
import { Album } from '../album.model';
import { GenreService } from '../genre.service';
import { ContentService } from '../content.service';

@Component({
  selector: 'app-discover-content',
  standalone: false,
  templateUrl: './discover-content.component.html',
  styleUrls: ['./discover-content.component.css']
})
export class DiscoverContentComponent implements OnInit {
  genres: string[] = [];
  albums: any[] = [];
  artists: any[] = [];
  selectedGenre: string | null = null;
  selectedAlbum: Album = {
    title: '',
    description: '',
    coverImage: '',
    releaseDate: new Date(),
    songs: [],
    artists: [],
    genres: [],
    id: ''
  };
  selectedArtist: string | null = null;

  constructor(
    private genreService: GenreService,
    private contentService: ContentService
  ) {}

  ngOnInit(): void {
    this.genreService.getAllGenres().subscribe({
      next: (genres: string[]) => {
        this.genres = genres;
        console.log(genres)
      },
      error: (err) => {
        console.error('Error while loading genres:', err);
      }
    });
  }

  selectGenre(genre: string) {
    const trimmedGenre = genre.trim();
    if (this.selectedGenre === trimmedGenre) {
      this.selectedGenre = null;
      this.artists = [];
      this.albums = [];
    } else {
      this.selectedGenre = trimmedGenre;
      this.fetchFilteredContent(trimmedGenre);
    }
  }

  fetchFilteredContent(genre: string) {
    this.genreService.getFilteredContent(genre).subscribe({
      next: (result) => {
        this.albums = result.albums;
        this.artists = result.artists;
      },
      error: (err) => {
        console.error("Error fetching filtered content:", err);
      }
    });
  }

  getArtistNames(artistIds: string[]): string {
    return artistIds ? artistIds.join(', ') : '';
  }

  getGenres(genres: string[]): string {
    return genres ? genres.join(', ') : '';
  }

  playAlbum() {
    console.log('Playing album:', this.selectedAlbum.title);
  }

  onCoverError() {
    // TODO: fallback image logic
  }
}
