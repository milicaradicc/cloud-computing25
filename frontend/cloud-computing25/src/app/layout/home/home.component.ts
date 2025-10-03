import { Component, OnInit } from '@angular/core';
import { FeedService } from '../feed.service';
import { Song } from '../../content/models/song.model';
import { Album } from '../../content/models/album.model';
import { Artist } from '../../artists/artist.model';


// Definišemo kako izgleda kompletan odgovor sa /feed endpointa
interface FeedResponse {
  recommendedSongs: Song[];
  recommendedAlbums: Album[];
}


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  standalone: false,
})
export class HomeComponent implements OnInit {

  songs: Song[] = [];
  albums: Album[] = [];
  isLoading = true;
  error: string | null = null;
  topArtistId: string | null = null;

  constructor(private feedService: FeedService) { }

  ngOnInit() {
    this.isLoading = true;
    this.feedService.getPersonalizedFeed().subscribe({
      next: (data) => {
        this.albums = data.albums || [];
        this.songs = data.songs || [];
        console.log(this.albums);

        if (data.topArtist?.Content) {
          this.topArtistId = data.topArtist.Content.split('#')[1] || null;
        }

        this.isLoading = false; 
      },
      error: (err) => {
        console.error("Greška pri dobavljanju feed-a:", err);
        this.error = "Došlo je do greške pri dobavljanju feed-a.";
        this.isLoading = false; 
      }
    });
  }

}
