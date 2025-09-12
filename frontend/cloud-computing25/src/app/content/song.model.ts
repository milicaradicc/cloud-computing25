import { Artist } from "../artists/artist.model";

export interface Song {
  title: string;
  file: File;
  fileType: string;
  fileSize: number;
  createdAt: Date;
  updatedAt: Date;
  genres?: string[];
  coverImage?: File;
  artists: Artist[];
}