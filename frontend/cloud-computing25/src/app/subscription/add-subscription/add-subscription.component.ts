import { Component, OnInit } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ArtistService } from '../../artists/artist.service';
import { AuthService } from '../../infrastructure/auth/auth.service';
import { CreateSubscriptionDto } from '../create-subscription-dto.model';
import { Artist } from '../../artists/artist.model';

@Component({
  selector: 'app-add-subscription',
  standalone: false,
  templateUrl: './add-subscription.component.html',
  styleUrls: ['./add-subscription.component.css']
})
export class AddSubscriptionComponent implements OnInit {
  form: FormGroup;
  typeOptions: string[] = ['artist', 'genre'];
  artists: Artist[] = [];
  genres: string[] = ['Pop', 'Rock', 'Jazz', 'Hip-Hop', 'Electronic'];
  dropdownOptions: { id: string, name: string }[] | string[] = []; 

  constructor(
    private fb: FormBuilder,
    private artistService: ArtistService,
    private authService: AuthService,
    private dialogRef: MatDialogRef<AddSubscriptionComponent>
  ) {
    this.form = this.fb.group({
      type: ['artist', Validators.required],
      targetId: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadDropdownOptions();

    this.form.get('type')?.valueChanges.subscribe(() => {
      this.form.get('targetId')?.setValue('');
      this.loadDropdownOptions();
    });
  }

  loadDropdownOptions(): void {
    const type = this.form.get('type')?.value;

    if (type === 'artist') {
      this.artistService.getAll().subscribe({
        next: (data) => {
          this.artists = data;
          this.dropdownOptions = data.map(a => ({ id: a.Id, name: a.name }));
        },
        error: () => {
          this.artists = [];
          this.dropdownOptions = [];
        }
      });
    } else {
      this.dropdownOptions = this.genres;
    }
  }

  async submit(): Promise<void> {
    if (!this.form.valid) return;

    const value = this.form.value;
    const user = await this.authService.getUser();

    let targetName: string;
    if (value.type === 'artist') {
      const selectedArtist = this.artists.find(a => a.Id === value.targetId);
      targetName = selectedArtist ? selectedArtist.name : '';
    } else {
      targetName = value.targetId; 
    }

    const subscriptionDto: CreateSubscriptionDto = {
      userId: user.userId,
      targetId: value.targetId,
      type: value.type,
      targetName: targetName,
      email:user.username
    };

    this.dialogRef.close(subscriptionDto);
  }


  cancel(): void {
    this.dialogRef.close();
  }
}
