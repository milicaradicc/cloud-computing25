import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ContentService } from '../content.service';

@Component({
  selector: 'app-album-details',
  templateUrl: './album-details.component.html',
  styleUrls: ['./album-details.component.css'],
  standalone: false
})
export class AlbumDetailsComponent implements OnInit {

  album: Album = {
    Id: "",
    title: "",
    description: "",
    coverImage: "",
    releaseDate: new Date(),
    createdDate: "",
    modifiedDate: "",
    deleted: false,
    Genre: "",
    genres: [],
    artists: [],
    songs: []
  };

  constructor(
    private route: ActivatedRoute,
    private albumService: ContentService
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const albumId = params['id'];
      if (!albumId) {
        console.error('Album ID is undefined!');
        return;
      }
      this.loadAlbum(albumId);
    });
  }

  loadAlbum(albumId: string) {
    this.albumService.getAlbum(albumId).subscribe({
      next: (result: AlbumResponse) => {
        const mapped: Album = {
          Id: result.Id,
          title: result.title,
          description: result.description,
          coverImage: result.coverImage,
          releaseDate: new Date(result.releaseDate),
          createdDate: result.createdDate,
          modifiedDate: result.modifiedDate,
          deleted: result.deleted === "true",
          Genre: result.Genre,
          genres: result.genres || [],
          artists: (result.Artists || []).map(a => ({
            Id: a.Id,
            name: a.Name,
            biography: "",    
            genres: [],
            Genre: "",
            songs: (a.Songs || []).map(s => ({
              Id: s.Id,
              title: s.title,
              duration: s.duration,
              genres: s.genres || [],
              type: s.type,
              artists: s.artists || [],
              fileName: "",
              fileType: "",
              fileSize: 0,
              deleted: false
            }))
          })),
          songs: (result.Artists || []).flatMap(a =>
            (a.Songs || []).map(s => ({
              Id: s.Id,
              title: s.title,
              duration: s.duration,
              genres: s.genres || [],
              type: s.type,
              artists: s.artists || [],
              fileName: "",
              fileType: "",
              fileSize: 0,
              deleted: false
            }))
          )
        };

        this.album = mapped;
        console.log("Album mapped:", this.album);
      }
    });
  }

  formatTime(seconds: number): string {
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${min}:${sec < 10 ? '0' + sec : sec}`;
  }
}

export class AlbumResponse {
  Id!: string;
  title!: string;
  description!: string;
  coverImage!: string;
  releaseDate!: string;   
  createdDate!: string;
  modifiedDate!: string;
  deleted!: string;       
  Genre!: string;
  genres!: string[];
  artists!: string[];    
  Artists!: ArtistResponse[];
}

export class ArtistResponse {
  Id!: string;
  Name!: string;
  Songs!: SongResponse[];
}

export class SongResponse {
  Id!: string;
  title!: string;
  duration!: number;
  genres!: string[];
  type!: string;
  artists!: SongArtistResponse[];
}

export class SongArtistResponse {
  Id!: string;
  name!: string;
}

export interface Album {
  Id: string;
  title: string;
  description: string;
  coverImage: string;
  releaseDate: Date;
  createdDate: string;
  modifiedDate: string;
  deleted: boolean;
  Genre: string;
  genres: string[];
  artists: Artist[];
  songs: Song[];
}

export interface Artist {
  Id: string;
  name: string;
  biography?: string;
  genres: string[];
  Genre: string;
  songs: Song[];
}

export interface Song {
  Id: string;
  title: string;
  duration: number;
  genres: string[];
  type: string;
  artists: SongArtist[];
  fileName?: string;
  fileType?: string;
  fileSize?: number;
  deleted: boolean;
}

export interface SongArtist {
  Id: string;
  name: string;
}
