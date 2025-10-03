import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CreateArtistDto } from '../create-artist-dto.model';
import { Artist } from '../artist.model';

@Component({
  selector: 'app-create-artist',
  standalone: false,
  templateUrl: './create-artist.component.html',
  styleUrls: ['./create-artist.component.css']
})
export class CreateArtistComponent implements OnInit {
  availableGenres: string[] = [
    'Pop', 'Rock', 'Hip Hop', 'Rap', 'Electronic', 
    'Classical', 'Jazz', 'Blues', 'Country', 'Reggae'
  ];

  createForm: FormGroup = new FormGroup({
    name: new FormControl('', [Validators.required]),
    biography: new FormControl('', [Validators.required]),
    genres: new FormControl([], [Validators.required]),
  });

  constructor(
    public dialogRef: MatDialogRef<CreateArtistComponent>,
    @Inject(MAT_DIALOG_DATA) public data: Artist | null
  ) {}

  ngOnInit(): void {
    if (this.data) {
      this.createForm.patchValue({
        name: this.data.name,
        biography: this.data.biography,
        genres: this.data.genres
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onSave(): void {
    if (this.createForm.valid) {
      const artist: CreateArtistDto = {
        name: this.createForm.value.name,
        biography: this.createForm.value.biography,
        genres: this.createForm.value.genres
      };
      this.dialogRef.close(artist);
    }
  }
}
