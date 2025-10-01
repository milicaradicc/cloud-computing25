import { Component, OnInit } from '@angular/core';
import { ContentService } from '../content.service';
import { GenreService } from '../../layout/genres.service';
import { Album } from '../models/album.model';

@Component({
  selector: 'app-discover-content',
  standalone: false,
  templateUrl: './discover-content.component.html',
  styleUrl: './discover-content.component.css'
})
export class DiscoverContentComponent implements OnInit {

  genres: string[] = [
    'Pop', 'Rock', 'Hip Hop', 'Rap', 'Electronic', 
    'Classical', 'Jazz', 'Blues', 'Country', 'Reggae'
  ];
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
    Id: '',
    Genre: '',
    deleted: false
  };
  selectedArtist: string | null = null;

  constructor(
    private genreService: GenreService,
    private contentService: ContentService
  ) {}

  ngOnInit(): void {
    // this.genreService.getAllGenres().subscribe({
    //   next: (genres: string[]) => {
    //     this.genres = genres;
    //     console.log(genres)
    //   },
    //   error: (err) => {
    //     console.error('Error while loading genres:', err);
    //   }
    // });
  }

  selectGenre(genre: string) {
    // Pretvori svaku reč tako da počinje velikim slovom
    const formattedGenre = genre
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');

    console.log(formattedGenre);

    if (this.selectedGenre === formattedGenre) {
      this.selectedGenre = null;
      this.artists = [];
      this.albums = [];
    } else {
      this.selectedGenre = formattedGenre;
      this.fetchFilteredContent(formattedGenre);
    }
  }

  fetchFilteredContent(genre: string) {
    this.genreService.getFilteredContent(genre).subscribe({
      next: (result) => {
        this.albums = result.albums;
        this.artists = result.artists;
        console.log(result)
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
