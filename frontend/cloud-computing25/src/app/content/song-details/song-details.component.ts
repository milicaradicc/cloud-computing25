import {Component, ElementRef, inject, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {ContentService} from '../content.service';
import {MatSnackBar} from '@angular/material/snack-bar';
import {Song} from '../song.model';
import {Rating} from '../rating.model';
import {environment} from '../../../env/environment';
import { AuthService } from '../../infrastructure/auth/auth.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-song-details',
  standalone: false,
  templateUrl: './song-details.component.html',
  styleUrl: './song-details.component.css'
})
export class SongDetailsComponent implements OnInit, OnDestroy {
  snackBar: MatSnackBar = inject(MatSnackBar)
  song: Song | null = null;
  @ViewChild('audioPlayer') audioPlayer!: ElementRef<HTMLAudioElement>;
  isPlaying = false;
  currentTime = 0;
  volume = 70;
  
  currentRating = 0;
  hoveredRating = 0;
  isRatingLoading = false;
  
  isLoadingSong = true;
  id = ""; // song
  
  private subscriptions = new Subscription();

  constructor(
    private route: ActivatedRoute,
    private contentService: ContentService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    const routeSubscription = this.route.params.subscribe(params => {
      this.id = params['id'];
      
      if (this.id) {
        this.loadSongDetails(this.id);
      } else {
        this.snackBar.open('No song ID provided', 'OK', { duration: 3000 });
      }
    });
    
    this.subscriptions.add(routeSubscription);
  }

  private loadSongDetails(id: string): void {
    this.isLoadingSong = true;
    this.song = null;
    
    const songSubscription = this.contentService.getSong(id).subscribe({
      next: (song: Song) => {
        console.log('Received song data:', song);
        this.song = song;
        this.isLoadingSong = false;
        
        this.loadSongRating();
      },
      error: (error) => {
        console.error('Error fetching song:', error);
        this.snackBar.open('Error loading song details', 'OK', { duration: 5000 });
        this.isLoadingSong = false;
      }
    });
    
    this.subscriptions.add(songSubscription);
  }

  private async loadSongRating(): Promise<void> {
    if (!this.song) return;
    
    try {
      const user = await this.authService.getUser();
      
      const ratingSubscription = this.contentService.getSongRating(this.id, user.userId).subscribe({
        next: (rating: Rating) => {
          this.currentRating = rating?.rating ?? 0;
          console.log('Current rating:', this.currentRating); 
        },
        error: (error) => {
          console.warn('No rating found or error loading rating:', error);
          this.currentRating = 0;
        }
      });
      
      this.subscriptions.add(ratingSubscription);
    } catch (error) {
      console.error('Error getting user for rating:', error);
      this.currentRating = 0;
    }
  }

  ngOnDestroy() {
    this.subscriptions.unsubscribe();
    
    if (this.audioPlayer?.nativeElement) {
      this.audioPlayer.nativeElement.pause();
    }
  }

  getAudioUrl(): string {
    if (!this.song?.fileName) return '';
    console.log(environment.s3BucketLink + '/' + this.song.fileName)
    return environment.s3BucketLink + '/' + this.song.fileName;
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

  onStarHover(rating: number) {
    this.hoveredRating = rating;
  }

  onStarLeave() {
    this.hoveredRating = 0;
  }

  async onStarClick(rating: number) {
    if (!this.song || this.isRatingLoading) return;

    this.isRatingLoading = true;

    try {
      const user = await this.authService.getUser();

      const ratingData: Rating = {
        userId: user.userId,
        targetId: this.id,
        rating: rating,
        ratedAt: Date.now()
      };

      console.log(ratingData);

      const ratingSubscription = this.contentService.rateSong(ratingData).subscribe({
        next: (response) => {
          this.currentRating = rating;
          this.snackBar.open('Rating submitted successfully!', 'OK', { duration: 3000 });
          this.isRatingLoading = false;
        },
        error: (error) => {
          this.snackBar.open('Error submitting rating', 'OK', { duration: 5000 });
          this.isRatingLoading = false;
          console.error('Rating error:', error);
        }
      });

      this.subscriptions.add(ratingSubscription);
    } catch (error) {
      this.isRatingLoading = false;
      console.error("Error getting user:", error);
    }
  }

  getStarClass(starNumber: number): string {
    const displayRating = this.hoveredRating || this.currentRating;
    return starNumber <= displayRating ? 'star-filled' : 'star-empty';
  }

  getStarArray(): number[] {
    return [1, 2, 3, 4, 5];
  }
}