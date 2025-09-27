import { Component, Inject } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Song } from '../song.model';
import { ContentService } from '../content.service';

@Component({
  selector: 'app-update-song',
  standalone: false,
  templateUrl: './update-song.component.html',
  styleUrls: ['./update-song.component.css']
})
export class UpdateSongComponent {
  form: FormGroup;
  selectedFile: File | null = null;

  constructor(
    private fb: FormBuilder,
    private contentService: ContentService,
    private dialogRef: MatDialogRef<UpdateSongComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { song: Song }
  ) {
    this.form = this.fb.group({
      title: [data.song.title, Validators.required],
      description: [data.song.description],
      coverImage: [data.song.coverImage],
      artists: [data.song.artists.map(a => a.Id), Validators.required],
      genres: [data.song.genres || []]
    });
  }

  onFileChange(event: any): void {
    const file = event.target.files[0];
    if (file) this.selectedFile = file;
  }

  async save(): Promise<void> {
    if (this.form.invalid) return;

    let fileBase64: string | undefined;
    if (this.selectedFile) {
      fileBase64 = await this.convertFileToBase64(this.selectedFile);
    }

    const updatedSong: any = {
      ...this.data.song,
      ...this.form.value,
      modifiedDate: new Date()
    };

    if (fileBase64) {
      updatedSong.fileBase64 = fileBase64;
      updatedSong.fileName = crypto.randomUUID();
      updatedSong.fileType = this.selectedFile!.type;
      updatedSong.fileSize = this.selectedFile!.size;
    }

    this.contentService.updateSong(updatedSong).subscribe({
      next: () => this.dialogRef.close(true),
      error: (err) => console.error('Update song failed', err)
    });
  }

  private convertFileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve((reader.result as string).split(',')[1]);
      reader.onerror = err => reject(err);
      reader.readAsDataURL(file);
    });
  }
}
