import { Injectable } from '@angular/core';
import { environment } from '../../env/environment';

@Injectable({
  providedIn: 'root'
})
export class S3UrlService {
  private readonly s3BaseUrl = environment.s3BucketLink;

  getImageUrl(s3Key: string | null | undefined): string | null {
    if (!s3Key) return null;
    
    if (s3Key.startsWith('http://') || s3Key.startsWith('https://')) {
      return s3Key;
    }
    
    return `${this.s3BaseUrl}/${s3Key}`;
  }


  getPresignedUrl(s3Key: string): string {
    return this.getImageUrl(s3Key) || '';
  }
  
  getDefaultCoverImage(): string {
    return 'assets/images/default-cover.png';
  }
}