import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subscription } from '../subscription.model';
import { AddSubscriptionComponent } from '../add-subscription/add-subscription.component';
import { CreateSubscriptionDto } from '../create-subscription-dto.model';
import { SubscriptionService } from '../subscription.service';
import { ArtistService } from '../../artists/artist.service';
import { AuthService } from '../../infrastructure/auth/auth.service';

@Component({
  selector: 'app-subscriptions',
  standalone: false,
  templateUrl: './subscriptions.component.html',
  styleUrls: ['./subscriptions.component.css']
})
export class SubscriptionsComponent implements OnInit {
  subscriptions: Subscription[] = [];
  userId!: string; 

  constructor(
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private artistService: ArtistService,
    private authService: AuthService,
    private subscriptionService: SubscriptionService
  ) {}

  async ngOnInit(): Promise<void> {
    const user = await this.authService.getUser();  
    this.userId = user.userId; 
    this.loadSubscriptions(this.userId);
  }

  loadSubscriptions(userId: string): void {
    this.subscriptionService.getSubscriptionsByUser(userId).subscribe({
      next: (subs) => {
        this.subscriptions = subs;
      },
      error: () => {
        this.snackBar.open('Error while loading subscriptions.', 'Close', { duration: 2000 });
      }
    });
  }

  openAddDialog(): void {
    const dialogRef = this.dialog.open(AddSubscriptionComponent, { width: '400px' });

    dialogRef.afterClosed().subscribe((result: CreateSubscriptionDto | undefined) => {
      if (!result) return;

      this.subscriptionService.add(result).subscribe({
        next: (newSub) => {
          this.subscriptions.push(newSub);
          this.snackBar.open('Subscription successfully added!', 'Close', { duration: 2000 });
          this.loadSubscriptions(this.userId); 
        },
        error: () => {
          this.snackBar.open('Error while adding subscription.', 'Close', { duration: 2000 });
        }
      });
    });
  }

  removeSubscription(sub: Subscription): void {
    this.subscriptionService.delete(sub).subscribe({
      next: () => {
        this.subscriptions = this.subscriptions.filter(s => s.id !== sub.id);
        this.snackBar.open('Subscription deleted.', 'Close', { duration: 2000 });
      },
      error: () => {
        this.snackBar.open('Error while deleting subscription.', 'Close', { duration: 2000 });
      }
    });
  }
}
