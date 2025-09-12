export interface FileInfo {
  fileName: string;
  fileType: string;
  fileSize: number;
  createdDate: Date;
  modifiedDate: Date;
  duration?: number;
}

export interface SingleUploadDTO {
  filename: string;
  fileBase64: string;
  title: string;
  description?: string;
  releaseDate: string;
  artists: number[];
  genres: string[];
  fileInfo?: FileInfo;
}