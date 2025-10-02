import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ArtistService } from '../artist.service';
import { Artist } from '../artist.model';
import { Album } from '../../content/models/album.model';

@Component({
  selector: 'app-artist-page',
  templateUrl: './artist-page.component.html',
  styleUrls: ['./artist-page.component.css'],
  standalone: false,
})
export class ArtistPageComponent implements OnInit {

  artistId?: string | null;
  artist: Artist | null = null;  // inicijalno null
  albums: Album[] = [];
  loading = true;
  errorAlbums: string | null = null;
  favoriteArtists: string[] = [];

  constructor(private route: ActivatedRoute, private artistService: ArtistService) {}

  ngOnInit(): void {
    this.artistId = this.route.snapshot.paramMap.get('id');
    
    if (this.artistId) {
      this.loadArtistWithAlbums(this.artistId);
    }
  }

loadArtistWithAlbums(id: string): void {
  this.loading = true;
  this.artistService.get(id).subscribe({
    next: (data) => {
      // Mapiranje artista
      this.artist = {
        Id: data.artist.Id,
        name: data.artist.name,
        biography: data.artist.biography,
        genres: data.artist.genres || [],
        Genre: data.artist.Genre
      };

      // Mapiranje albuma
      this.albums = (data.albums || []).map((album: any) => ({
        Id: album.Id,
        title: album.title,
        description: album.description,
        coverImage: album.coverImage,
        releaseDate: new Date(album.releaseDate), // pretvori u Date
        songs: [], // moze se popuniti kasnije ako ima songs endpoint
        artists: (album.artists || []).map((artistId: string) => ({
          Id: artistId,
          name: "",       // po potrebi se moze fetchovati detaljno
          biography: "",
          genres: [],
          Genre: ""
        })),
        genres: album.genres || [],
        Genre: album.Genre,
        deleted: album.deleted === "true" // string u boolean
      }));

      this.loading = false;
      console.log('Mapped artist:', this.artist);
      console.log('Mapped albums:', this.albums);
    },
    error: (err) => {
      console.error(err);
      this.errorAlbums = 'Failed to load artist or albums';
      this.loading = false;
    }
  });
}


  isFavorite(artist: Artist): boolean {
    return this.favoriteArtists.includes(artist.Id);
  }

  toggleFavorite(artist: Artist): void {
    if (this.isFavorite(artist)) {
      this.favoriteArtists = this.favoriteArtists.filter(id => id !== artist.Id);
    } else {
      this.favoriteArtists.push(artist.Id);
    }
  }
}
