import { Artist } from "../artists/artist.model";

export interface SingleUploadDTO {
  fileName: string;
  fileType: string;
  fileSize: number;
  createdDate: Date;
  modifiedDate: Date;
  duration?: number;
  fileBase64: string;
  title: string;
  description?: string;
  artists: Artist[];
  genres: string[];
  album: string,
  coverImage: string;
  single: boolean
}