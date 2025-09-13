import { Component, OnInit } from '@angular/core';
import { Song } from '../song.model';
import { Album } from '../album.model';
import { ContentService } from '../content.service';

@Component({
  selector: 'app-content',
  standalone: false,
  templateUrl: './content.component.html',
  styleUrls: ['./content.component.css']
})
export class ContentComponent implements OnInit {
  songs: Song[] = [];
  albums: Album[] = [];
  loadingSongs: boolean = true;
  loadingAlbums: boolean = true;
  errorSongs: string | null = null;
  errorAlbums: string | null = null;

  constructor(private contentService: ContentService) { }

  ngOnInit(): void {
    this.loadSongs();
    this.loadAlbums();
  }

  loadSongs() {
    this.contentService.getAllSongs().subscribe({
      next: data => {
        this.songs = data;
        this.loadingSongs = false;
      },
      error: err => {
        console.error(err);
        this.errorSongs = 'Failed to load songs';
        this.loadingSongs = false;
      }
    });
  }

  loadAlbums() {
    this.contentService.getAllAlbums().subscribe({
      next: data => {
        this.albums = data;
        this.loadingAlbums = false;
      },
      error: err => {
        console.error(err);
        this.errorAlbums = 'Failed to load albums';
        this.loadingAlbums = false;
      }
    });
  }

  getArtistNames(artists: any[] | undefined): string {
    if (!artists || artists.length === 0) return '';
    return artists.map(a => a.name).join(', ');
  }
}
