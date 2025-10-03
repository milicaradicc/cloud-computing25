export interface Subscription {
    id: string;
    User: string;
    Target: string;
    type: 'artist' | 'genre';
    createdAt: number; 
    targetName?: string;
}