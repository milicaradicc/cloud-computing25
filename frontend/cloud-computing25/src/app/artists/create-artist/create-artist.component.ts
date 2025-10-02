import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { CreateArtistDto } from '../create-artist-dto.model';

@Component({
  selector: 'app-create-artist',
  standalone: false,
  templateUrl: './create-artist.component.html',
  styleUrls: ['./create-artist.component.css']
})
export class CreateArtistComponent {
  availableGenres: string[] = [
    'Pop', 'Rock', 'Hip Hop', 'Rap', 'Electronic', 
    'Classical', 'Jazz', 'Blues', 'Country', 'Reggae'
  ];

  createForm: FormGroup = new FormGroup({
    name: new FormControl('', [Validators.required]),
    biography: new FormControl('', [Validators.required]),
    genres: new FormControl([], [Validators.required]), // inicijalno prazan niz
  });

  constructor(public dialogRef: MatDialogRef<CreateArtistComponent>) {}

  onCancel(): void {
    this.dialogRef.close();
  }

  onSave(): void {
    if (this.createForm.valid) {
      const artist: CreateArtistDto = {
        name: this.createForm.value.name,
        biography: this.createForm.value.biography,
        genres: this.createForm.value.genres // već je niz
      };
      this.dialogRef.close(artist);
    }
  }
}
