export interface Rating {
  targetId: string | number;  // The ID of the song being rated
  rating: number;             // The rating value (1-5)
  userId?: string | number;   // Optional: User ID if not handled by backend
  createdAt?: Date;           // Optional: Timestamp
  updatedAt?: Date;           // Optional: Last updated timestamp
}