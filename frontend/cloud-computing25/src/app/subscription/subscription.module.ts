import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { SubscriptionsComponent } from './subscriptions/subscriptions.component';
import { AddSubscriptionComponent } from './add-subscription/add-subscription.component';
import { ReactiveFormsModule } from '@angular/forms';

@NgModule({
  declarations: [
    SubscriptionsComponent,
    AddSubscriptionComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,  // <-- dodaj ovo
    MatTableModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatSnackBarModule,
  ],
  exports: [
    SubscriptionsComponent
  ]
})
export class SubscriptionModule {}
