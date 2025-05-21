import { db, Release } from './db';

export const seedReleaseData = async () => {
  // Check if we already have releases
  const releaseCount = await db.releases.count();
  if (releaseCount > 0) {
    console.log('Release data already exists, skipping seed');
    return;
  }

  console.log('Seeding release data...');

  const releases: Release[] = [
    {
      version: '1.2.0',
      releaseDate: new Date('2025-04-25'),
      title: 'April 2025 Update',
      description:
        'This update brings several new features and improvements to the Poly Micro Manager.',
      isLatest: 1,
      changes: [
        {
          type: 'feature',
          description: 'Added new microservice testing capabilities with improved UI',
        },
        {
          type: 'feature',
          description: 'Introduced automatic release management system',
        },
        {
          type: 'improvement',
          description: 'Enhanced dashboard performance and responsiveness',
        },
        {
          type: 'fix',
          description: 'Fixed authentication issues when logging in with certain email providers',
        },
      ],
    },
    {
      version: '1.1.0',
      releaseDate: new Date('2025-03-15'),
      title: 'March 2025 Update',
      description:
        'This update focuses on improving the monitoring capabilities and fixing several bugs.',
      isLatest: 0,
      changes: [
        {
          type: 'feature',
          description: 'Added real-time monitoring dashboard',
        },
        {
          type: 'improvement',
          description: 'Optimized microservice discovery process',
        },
        {
          type: 'fix',
          description: 'Fixed issue with project selection in the dashboard',
        },
      ],
    },
    {
      version: '1.0.0',
      releaseDate: new Date('2025-02-01'),
      title: 'Initial Release',
      description: 'The first stable release of Poly Micro Manager.',
      isLatest: 0,
      changes: [
        {
          type: 'feature',
          description: 'Core microservice management functionality',
        },
        {
          type: 'feature',
          description: 'Basic authentication and user management',
        },
        {
          type: 'feature',
          description: 'Project configuration and setup',
        },
      ],
    },
  ];

  // Add releases to the database
  for (const release of releases) {
    await db.releases.add(release);
  }

  console.log('Release data seeded successfully');
};

export default seedReleaseData;
