import { Injectable } from '@angular/core';
import Dexie from 'dexie';

@Injectable({
  providedIn: 'root'
})
export class IndexedDbService extends Dexie {

  private songs!: Dexie.Table<SongDb, string>; // string = songId

  constructor() {
    super('OfflineSongsDB');

    // Definišemo shemu baze: key = songId
    this.version(1).stores({
      songs: 'id,title,metadata'
    });

    this.songs = this.table('songs');
  }

  // Proverava da li je pesma keširana
  async isSongCached(songId: string): Promise<boolean> {
    const song = await this.songs.get(songId);
    return !!song;
  }

  // Čuva pesmu u IndexedDB
  async saveSong(songId: string, blob: Blob, metadata: any): Promise<void> {
    await this.songs.put({ id: songId, blob, title: metadata.title, metadata });
  }

  // Briše pesmu iz IndexedDB
  async deleteSong(songId: string): Promise<void> {
    await this.songs.delete(songId);
  }

  // Dohvata pesmu za reprodukciju
  async getSongBlob(songId: string): Promise<Blob | null> {
    const song = await this.songs.get(songId);
    return song?.blob || null;
  }

  // Dohvata sve pesme iz IndexedDB
  async getAllSongs(): Promise<SongDb[]> {
    return await this.songs.toArray();
  }

}

// Interfejs za tabelu
interface SongDb {
  id: string;
  title: string;
  blob: Blob;
  metadata: any;
}
