export interface AlbumUploadDTO {
  createdDate: Date;
  modifiedDate: Date;
  title: string;
  description?: string;
  artists: number[];
  genres: string[];
  coverFileBase64?: string;
  coverFileName?: string;
  single: boolean
}
