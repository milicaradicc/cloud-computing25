import {Component, ElementRef, inject, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ContentService} from '../content.service';
import {MatSnackBar} from '@angular/material/snack-bar';
import {Song} from '../song.model';
import {environment} from '../../../env/environment';

@Component({
  selector: 'app-song-details',
  standalone: false,
  templateUrl: './song-details.component.html',
  styleUrl: './song-details.component.css'
})
export class SongDetailsComponent implements OnInit, OnDestroy {
  snackBar:MatSnackBar = inject(MatSnackBar)
  song: Song | null = null;
  @ViewChild('audioPlayer') audioPlayer!: ElementRef<HTMLAudioElement>;
  isPlaying = false;
  currentTime = 0;
  volume = 70;

  constructor(
    private route: ActivatedRoute,
    private contentService: ContentService,){}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const id = params['id'];
      this.contentService.getSong(id).subscribe({
        next: (song:Song) => {
          this.song=song;
          console.log(song);
        },
        error: (err) => {
          this.snackBar.open('Error fetching song','OK',{duration:5000});
        }
      });
    })
  }

  ngOnDestroy() {
    if (this.audioPlayer?.nativeElement) {
      this.audioPlayer.nativeElement.pause();
    }
  }

  getAudioUrl(): string {
    return environment.s3BucketLink+this.song?.fileName;
  }

  togglePlayPause() {
    if (!this.audioPlayer?.nativeElement) return;

    if (this.isPlaying) {
      this.audioPlayer.nativeElement.pause();
    } else {
      this.audioPlayer.nativeElement.play();
    }
    this.isPlaying = !this.isPlaying;
  }

  previousTrack() {
    // Implement previous track logic
    console.log('Previous track');
  }

  nextTrack() {
    // Implement next track logic
    console.log('Next track');
  }

  setVolume(event: any) {
    this.volume = event.target.value;
    if (this.audioPlayer?.nativeElement) {
      this.audioPlayer.nativeElement.volume = this.volume / 100;
    }
  }

  onAudioLoaded() {
    if (this.audioPlayer?.nativeElement) {
      this.audioPlayer.nativeElement.volume = this.volume / 100;
    }
  }

  onTimeUpdate() {
    if (this.audioPlayer?.nativeElement) {
      this.currentTime = this.audioPlayer.nativeElement.currentTime;
    }
  }

  onAudioEnded() {
    this.isPlaying = false;
    this.currentTime = 0;
  }

  getProgressPercentage(): number {
    if (!this.song?.duration || !this.currentTime) return 0;
    return (this.currentTime / this.song.duration) * 100;
  }

  formatTime(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  seekTo(event: MouseEvent) {
    if (!this.audioPlayer?.nativeElement || !this.song?.duration) return;

    const progressBar = event.currentTarget as HTMLElement;
    const rect = progressBar.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const percentage = clickX / rect.width;
    const newTime = percentage * this.song.duration;

    this.audioPlayer.nativeElement.currentTime = newTime;
    this.currentTime = newTime;
  }
}
