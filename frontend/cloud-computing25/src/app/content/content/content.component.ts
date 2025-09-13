import { Component, OnInit } from '@angular/core';
import { Song } from '../song.model';
import { ContentService } from '../content.service';

@Component({
  selector: 'app-content',
  standalone: false,
  templateUrl: './content.component.html',
  styleUrls: ['./content.component.css']
})
export class ContentComponent implements OnInit {
  songs: Song[] = [];
  loading: boolean = true;
  error: string | null = null;

  constructor(private contentService: ContentService) { }

  ngOnInit(): void {
    this.contentService.getAllSongs().subscribe({
      next: (data) => {
        console.log("Songs from API:", data);
        this.songs = data;
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.error = "Failed to load songs";
        this.loading = false;
      }
    });
  }
  getArtistNames(artists: any[] | undefined): string {
  if (!artists || artists.length === 0) return '';
  return artists.map(a => a.name).join(', ');
}
}
