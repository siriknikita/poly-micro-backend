import Dexie, { Table, IndexableType } from 'dexie';

export interface User {
  id?: IndexableType;
  businessName: string;
  email: string;
  username: string;
  password: string;
  hasCompletedOnboarding?: boolean;
}

export interface Release {
  id?: IndexableType;
  version: string;
  releaseDate: Date;
  title: string;
  description: string;
  changes: ReleaseChange[];
  isLatest: number; // Using 1 for true, 0 for false to work better with Dexie indexing
}

export interface ReleaseChange {
  type: 'feature' | 'fix' | 'improvement' | 'breaking';
  description: string;
}

export interface UserAcknowledgment {
  id?: IndexableType;
  userId: IndexableType;
  releaseId: IndexableType;
  acknowledgedAt: Date;
}

export class AppDatabase extends Dexie {
  users!: Table<User>;
  releases!: Table<Release>;
  userAcknowledgments!: Table<UserAcknowledgment>;

  constructor() {
    super('AppDatabase');
    this.version(3).stores({
      users: '++id, username, email, hasCompletedOnboarding',
      releases: '++id, version, releaseDate, isLatest',
      userAcknowledgments: '++id, userId, releaseId',
    });
  }
}

export const db = new AppDatabase();
