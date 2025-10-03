import {Component, inject, OnInit, ViewChild} from '@angular/core';
import {ArtistService} from '../artist.service';
import {MatDialog} from '@angular/material/dialog';
import {MatTableDataSource} from '@angular/material/table';
import {Artist} from '../artist.model';
import {MatSnackBar} from '@angular/material/snack-bar';
import {MatSort} from '@angular/material/sort';
import {CreateArtistComponent} from '../create-artist/create-artist.component';
import { FeedService } from '../../layout/feed.service';

@Component({
  selector: 'app-artists',
  standalone: false,
  templateUrl: './artists.component.html',
  styleUrl: './artists.component.css',
})
export class ArtistsComponent implements OnInit {
  constructor(private service:ArtistService,
              private dialog: MatDialog) {}

  dataSource: MatTableDataSource<Artist> = new MatTableDataSource<Artist>([]);
  displayedColumns: string[] = ['name', 'biography','genres','actions']; 
  snackBar:MatSnackBar = inject(MatSnackBar);
  @ViewChild(MatSort) sort!: MatSort;


  ngOnInit(): void {
    this.refreshDataSource();
  }

  private refreshDataSource() {
    this.service.getAll().subscribe({
      next: (artists: Artist[]) => {
        artists.sort((a, b) => a.name.localeCompare(b.name));
        console.log(artists)
        this.dataSource = new MatTableDataSource<Artist>(artists);
      }
    })
  }

  openAddArtistDialog() {
    const dialogRef = this.dialog.open(CreateArtistComponent, {
      width: '400px',
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.service.add(result).subscribe({
          next: (response) => {
            this.refreshDataSource();
            this.snackBar.open('Artist created successfully','OK',{duration:3000});
          },
        });
      }
    });
  }
openEditArtistDialog(artist: Artist) {
  const dialogRef = this.dialog.open(CreateArtistComponent, {
    width: '400px',
    data: artist 
  });

  dialogRef.afterClosed().subscribe(result => {
    if (result) {
      this.service.update(artist.Id, result).subscribe({
        next: () => {
          this.refreshDataSource();
          this.snackBar.open('Artist updated successfully','OK',{duration:3000});
        },
        error: (err) => {
          this.snackBar.open('Error updating artist','OK',{duration:3000});
          console.error(err);
        }
      });
    }
  });
}


  deleteArtist(artist: Artist) {
    if(confirm(`Are you sure you want to delete ${artist.name}?`)) {
      this.service.delete(artist.Id).subscribe({
        next: () => {
          this.refreshDataSource();
          this.snackBar.open('Artist deleted successfully','OK',{duration:3000});
        }
      });
    }
  }
}
