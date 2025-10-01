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
        this.artist = data.artist;
        this.albums = data.albums || [];

        this.loading = false;
        console.log('data:', data);
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
