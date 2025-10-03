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

  // Promenljive koje tvoj HTML template koristi
  recommendedSongs: Song[] = [];
  recommendedAlbums: Album[] = [];
  isLoading = true; // Počinjemo sa učitavanjem
  error: string | null = null;

  // Injektujemo FeedService da bismo mogli da pozivamo API
  constructor(private feedService: FeedService) { }

  /**
   * ngOnInit se izvršava automatski kada se komponenta inicijalizuje.
   * Ovde pozivamo naš servis da dobavi personalizovani feed.
   */
  ngOnInit(): void {
    this.feedService.getPersonalizedFeed().subscribe({
      // `next` se izvršava kada podaci uspešno stignu sa servera
      next: (data: FeedResponse) => {
        console.log('Podaci su uspešno stigli:', data);
        this.recommendedSongs = data.recommendedSongs || [];
        this.recommendedAlbums = data.recommendedAlbums || [];
        this.isLoading = false; // Završili smo sa učitavanjem
      },
      // `error` se izvršava ako dođe do greške prilikom poziva
      error: (err) => {
        console.error('Došlo je do greške prilikom dobavljanja feed-a:', err);
        this.error = 'Nismo uspeli da učitamo vaše preporuke. Molimo pokušajte ponovo kasnije.';
        this.isLoading = false; // Završili smo sa učitavanjem (iako neuspešno)
      }
    });
  }

  /**
   * Pomoćna funkcija koju tvoj HTML poziva da formatira imena izvođača za prikaz.
   * @param artists - Niz objekata izvođača
   * @returns String sa imenima izvođača odvojenim zarezom, ili null.
   */
  getArtistNames(artists?: Artist[]): string | null {
    if (!artists || artists.length === 0) {
      return null;
    }
    return artists.map(artist => artist.name).join(', ');
  }
}