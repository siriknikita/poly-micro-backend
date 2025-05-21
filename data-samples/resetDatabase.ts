import { db } from './db';
import { syncReleasesToDatabase } from '../utils/releaseSync';

/**
 * Resets the database by deleting all tables and reseeding with fresh data
 * @param syncSource 'local' or 'github' - where to sync releases from
 * @param path Optional path to the releases file or GitHub repository info
 */
export const resetDatabase = async (
  syncSource: 'local' | 'github' = 'local',
  path?: string,
): Promise<void> => {
  console.log('Resetting database...');

  try {
    // Delete all tables
    await db.releases.clear();
    await db.userAcknowledgments.clear();

    // Sync releases from the specified source
    await syncReleasesToDatabase(syncSource, path);

    console.log('Database reset successfully');
  } catch (error) {
    console.error('Error resetting database:', error);
  }
};

export default resetDatabase;
