import { Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ContentService } from '../content.service';
import { DownloadService } from '../download.service';
import { firstValueFrom } from 'rxjs'; // Dodati import za Observable ako nije prisutan
import { IndexedDbService } from '../indexed-db.service';
import { ListeningHistoryService } from '../listening-history.service';
import { environment } from '../../../env/environment';

@Component({
  selector: 'app-album-details',
  templateUrl: './album-details.component.html',
  styleUrls: ['./album-details.component.css'],
  standalone: false
})
export class AlbumDetailsComponent implements OnInit {

  isProcessing: boolean = false;
  isLoading = false; 

  cachedStatus: { [key: string]: boolean } = {}; 

  album: Album = {
    Id: "",
    title: "",
    description: "",
    coverImage: "",
    releaseDate: new Date(),
    createdDate: "",
    modifiedDate: "",
    deleted: false,
    Genre: "",
    genres: [],
    artists: [],
    songs: []
  };

  constructor(
    private route: ActivatedRoute,
    private albumService: ContentService,
    private downloadService: DownloadService, 
    private dbService: IndexedDbService,
    private router: Router,
    private listeningHistoryService: ListeningHistoryService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const albumId = params['id'];
      if (!albumId) {
        console.error('Album ID is undefined!');
        return;
      }
      this.loadAlbum(albumId);
    });
  }

  isSongCached(songId: string): boolean {
    return this.cachedStatus[songId] || false;
  }

  async checkAllSongsCacheStatus(songs: Song[]): Promise<void> {
    for (const song of songs) {
        const isCached = await this.dbService.isSongCached(song.Id);
        this.cachedStatus = { ...this.cachedStatus, [song.Id]: isCached };
    }
  }

  async toggleOfflineStatus(song: Song): Promise<void> {
    const songId = song.Id;
    const songTitle = song.title;

    if (this.isProcessing) return; 

    const isCurrentlyCached = this.isSongCached(songId);
    
    if (isCurrentlyCached) {
      await this.deleteSongFromCache(songId);
    } else {
      await this.cacheSong(songId, songTitle);
    }
    
    this.cachedStatus = { ...this.cachedStatus, [songId]: !isCurrentlyCached };
  }

  private async cacheSong(songId: string, songTitle: string): Promise<void> {
    console.log(`Starting caching for songId=${songId}, title=${songTitle}`);
    this.isProcessing = true;
    try {
      let presignedUrlResponse;
      try {
        presignedUrlResponse = await firstValueFrom(this.downloadService.getPresignedUrl(songId));
        console.log("Presigned URL response:", presignedUrlResponse);
      } catch (error) {
        console.error("Error getting presigned URL:", error);
        this.isProcessing = false;
        return;
      }

      if (!presignedUrlResponse) {
        console.error('Presigned URL nije dobijen!');
        this.isProcessing = false;
        return;
      }

      const presignedUrl = presignedUrlResponse.url;
      console.log("Fetching file from presigned URL:", presignedUrl);

      const fileResponse = await fetch(presignedUrl);
      console.log("Fetch response status:", fileResponse.status);

      if (!fileResponse.ok) throw new Error('Failed to fetch audio file from S3');

      const audioBlob = await fileResponse.blob();
      console.log("Audio blob size:", audioBlob.size);

      await this.dbService.saveSong(songId, audioBlob, { title: songTitle });
      console.log(`Song ${songTitle} (${songId}) successfully cached for offline.`);
    } catch (error) {
      console.error('Error during caching:', error);
    } finally {
      this.isProcessing = false;
    }
  }
  
  private async deleteSongFromCache(songId: string): Promise<void> {
      this.isProcessing = true;
      try {
          await this.dbService.deleteSong(songId);
          console.log(`Pesma ${songId} obrisana iz offline keša.`);
      } catch (error) {
          console.error('Greška pri brisanju iz keša:', error);
      } finally {
          this.isProcessing = false;
      }
  }

  onDownloadClick(songId?: string): void { 
    if (!songId) {
      console.error('Song ID is missing for download!');
      return;
    }

    this.isLoading = true;
    
    this.downloadService.downloadSong(songId).subscribe({ 
      next: (response) => {
        this.downloadService.initiateDownload(response.url, response.filename);
        this.isLoading = false; 
      },
      error: (err) => {
        console.error('Download error:', err);
        this.isLoading = false;
      }
    });
  }

  stopSong(): void {
    if (this.audioPlayer && this.audioPlayer.nativeElement) {
      this.audioPlayer.nativeElement.pause();   
      this.audioPlayer.nativeElement.currentTime = 0; 
    }
  }

  loadAlbum(albumId: string) {
    this.albumService.getAlbum(albumId).subscribe({
      next: (result: AlbumResponse) => {
        const songsMapped: Song[] = (result.Artists || []).flatMap(a =>
          (a.Songs || []).map(s => ({
            Id: s.Id,
            title: s.title,
            duration: s.duration,
            genres: s.genres || [],
            type: s.type,
            artists: s.artists || [],
            fileName: "",
            fileType: "",
            fileSize: 0,
            deleted: false
          }))
        );

        const mapped: Album = {
          Id: result.Id,
          title: result.title,
          description: result.description,
          coverImage: result.coverImage,
          releaseDate: new Date(result.releaseDate),
          createdDate: result.createdDate,
          modifiedDate: result.modifiedDate,
          deleted: result.deleted === "true",
          Genre: result.Genre,
          genres: result.genres || [],
          artists: (result.Artists || []).map(a => ({
             Id: a.Id, name: a.Name, biography: "", genres: [], Genre: "", songs: []
          })),
          songs: songsMapped
        };

        this.album = mapped;
        console.log("Album mapped:", this.album);
        
        this.checkAllSongsCacheStatus(songsMapped);
      }
    });
  }

  formatTime(seconds: number): string {
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${min}:${sec < 10 ? '0' + sec : sec}`;
  }

  async playOffline(songId: string, audioElement: HTMLAudioElement) {
    const blob = await this.dbService.getSongBlob(songId);
    if (blob) {
      const objectUrl = URL.createObjectURL(blob);
      audioElement.src = objectUrl;
      audioElement.play();
    } else {
      console.log('Pesma nije keširana, reprodukuj online');
    }
  }

  @ViewChild('audioPlayer') audioPlayer!: ElementRef<HTMLAudioElement>;

  async onOfflineButtonClick(song: Song, audioElement: HTMLAudioElement) {
    if (this.isProcessing) return;

    if (this.isSongCached(song.Id)) {
      const blob = await this.dbService.getSongBlob(song.Id);
      if (blob) {
        const objectUrl = URL.createObjectURL(blob);
        audioElement.src = objectUrl;
        audioElement.play();
        this.listeningHistoryService.recordListen(song.Id, this.album.Id).subscribe({
          next: () => console.log(`Beleži se slušanje za pesmu: ${song.title}`),
          error: (err) => console.error('Greška pri beleženju slušanja:', err)
        });
      }
    } else {
      await this.toggleOfflineStatus(song);
    }
  }

  goToSongDetails(songId: string): void {
    this.router.navigate(['/song-details', songId]);
  }
  getAlbumCoverUrl(): string {
    if (!this.album.coverImage) return "assets/default-album.png"; // fallback
    return `${environment.s3BucketLink}/${this.album.coverImage}`;
  }

  onAlbumImageError(event: Event) {
    const img = event.target as HTMLImageElement;
    img.src = 'assets/default-album.png';
  }
}

export class AlbumResponse {
  Id!: string;
  title!: string;
  description!: string;
  coverImage!: string;
  releaseDate!: string;    
  createdDate!: string;
  modifiedDate!: string;
  deleted!: string;        
  Genre!: string;
  genres!: string[];
  artists!: string[];      
  Artists!: ArtistResponse[];
}

export class ArtistResponse {
  Id!: string;
  Name!: string;
  Songs!: SongResponse[];
}

export class SongResponse {
  Id!: string;
  title!: string;
  duration!: number;
  genres!: string[];
  type!: string;
  artists!: SongArtistResponse[];
}

export class SongArtistResponse {
  Id!: string;
  name!: string;
}

export interface Album {
  Id: string;
  title: string;
  description: string;
  coverImage: string;
  releaseDate: Date;
  createdDate: string;
  modifiedDate: string;
  deleted: boolean;
  Genre: string;
  genres: string[];
  artists: Artist[];
  songs: Song[];
}

export interface Artist {
  Id: string;
  name: string;
  biography?: string;
  genres: string[];
  Genre: string;
  songs: Song[];
}

export interface Song {
  Id: string;
  title: string;
  duration: number;
  genres: string[];
  type: string;
  artists: SongArtist[];
  fileName?: string;
  fileType?: string;
  fileSize?: number;
  deleted: boolean;
}

export interface SongArtist {
  Id: string;
  name: string;
}