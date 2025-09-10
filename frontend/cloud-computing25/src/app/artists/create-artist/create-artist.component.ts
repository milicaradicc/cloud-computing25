import { Component } from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {ArtistService} from '../artist.service';
import { MatDialogRef } from '@angular/material/dialog';
import {CreateArtistDto} from '../create-artist-dto.model';

@Component({
  selector: 'app-create-artist',
  standalone: false,
  templateUrl: './create-artist.component.html',
  styleUrl: './create-artist.component.css'
})
export class CreateArtistComponent {
  createForm: FormGroup= new FormGroup({
    name: new FormControl('', [Validators.required]),
    biography: new FormControl('', [Validators.required]),
    genres: new FormControl('', [Validators.required]),
  });

  constructor(
    public dialogRef: MatDialogRef<CreateArtistComponent>
  ){}


  onCancel(): void {
    this.dialogRef.close();
  }

  onSave(): void {
    if(this.createForm.valid){
      const artist:CreateArtistDto={
        name:this.createForm.value.name,
        biography:this.createForm.value.biography,
        genres:this.createForm.value.genres.split(',')
      }
      this.dialogRef.close(artist);
    }
  }
}
