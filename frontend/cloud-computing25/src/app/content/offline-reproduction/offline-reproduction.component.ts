import { Component, ElementRef, Input, OnInit, ViewChild } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { Song } from '../album-details/album-details.component'; // prilagodi import
import { DownloadService } from '../download.service';
import { IndexedDbService } from '../indexed-db.service';
import { ListeningHistoryService } from '../listening-history.service';
import { FeedService } from '../../layout/feed.service';
import { openDB } from 'idb';

@Component({
  selector: 'app-offline-reproduction',
  standalone: false,
  templateUrl: './offline-reproduction.component.html',
  styleUrls: ['./offline-reproduction.component.css']
})
export class OfflineReproductionComponent implements OnInit {
  @Input() songs: Song[] = [];
  @Input() albumId!: string; 
  @Input() albumArtists: any[] = [];
  @Input() albumGenre!: string;

  isProcessing = false;
  isLoading = false;
  cachedStatus: { [key: string]: boolean } = {};

  @ViewChild('audioPlayer') audioPlayer!: ElementRef<HTMLAudioElement>;

  constructor(
    private dbService: IndexedDbService,
    private downloadService: DownloadService,
    private listeningHistoryService: ListeningHistoryService,
  ) {}

  ngOnInit(): void {
    this.checkAllSongsCacheStatus(this.songs);
    this.loadOfflineSongs();
  }

  async checkAllSongsCacheStatus(songs: Song[]): Promise<void> {
    for (const song of songs) {
      const isCached = await this.dbService.isSongCached(song.Id);
      this.cachedStatus = { ...this.cachedStatus, [song.Id]: isCached };
    }
  }

  async loadOfflineSongs(): Promise<void> {
    try {
      const offlineSongs = await this.dbService.getAllSongs(); 
      if (offlineSongs && offlineSongs.length > 0) {
        this.songs = offlineSongs.map((item: any) => ({
          Id: item.id,
          title: item.metadata?.title || 'Unknown',
          duration: item.metadata?.duration || 0,
          genres: item.metadata?.genres || [],
          type: item.metadata?.type || 'audio',
          artists: item.metadata?.artists || [],
          fileName: '',
          fileType: '',
          fileSize: item.blob?.size || 0,
          deleted: false
        }));
        offlineSongs.forEach((s: any) => {
          this.cachedStatus[s.id] = true;
        });
      }
    } catch (err) {
      console.error("Greška pri učitavanju offline pesama:", err);
    }
  }

  isSongCached(songId: string): boolean {
    return this.cachedStatus[songId] || false;
  }

  formatTime(seconds: number): string {
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${min}:${sec < 10 ? '0' + sec : sec}`;
  }

  async onOfflineButtonClick(song: Song) {
    if (this.isProcessing) return;

    const audioElement = this.audioPlayer.nativeElement;

    if (this.isSongCached(song.Id)) {
      const blob = await this.dbService.getSongBlob(song.Id);
      if (blob) {
        const objectUrl = URL.createObjectURL(blob);
        audioElement.src = objectUrl;
        await audioElement.play();
      }
    } else {
      await this.toggleOfflineStatus(song);
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
    this.isProcessing = true;
    try {
      let presignedUrlResponse = await firstValueFrom(this.downloadService.getPresignedUrl(songId));
      if (!presignedUrlResponse) return;

      const fileResponse = await fetch(presignedUrlResponse.url);
      if (!fileResponse.ok) throw new Error('Failed to fetch audio file from S3');

      const audioBlob = await fileResponse.blob();
      await this.dbService.saveSong(songId, audioBlob, { title: songTitle });
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
    } catch (error) {
      console.error('Greška pri brisanju iz keša:', error);
    } finally {
      this.isProcessing = false;
    }
  }

  stopSong(): void {
    const audioElement = this.audioPlayer.nativeElement;
    audioElement.pause();
    audioElement.currentTime = 0;
  }

  onDownloadClick(songId: string): void {
    if (!songId) return;
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
}
