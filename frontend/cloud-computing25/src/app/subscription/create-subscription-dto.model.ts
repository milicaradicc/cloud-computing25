export interface CreateSubscriptionDto {
    userId: string;
    targetId: string;
    type: 'artist' | 'genre';
    targetName?: string; // zanr ili naziv artista
    email?: string;
}