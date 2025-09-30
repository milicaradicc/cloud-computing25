export interface Rating {
  targetId: string;  // song (album?)
  rating: number;            
  userId: string;   
  ratedAt?: number;           
}