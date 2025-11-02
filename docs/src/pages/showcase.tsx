import React, {useState} from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import ShowcaseCard, {ShowcaseProject} from '@site/src/components/ShowcaseCard';
import styles from './showcase.module.css';

const PROJECTS: ShowcaseProject[] = [
  {
    title: 'abstract-backend-implementation-template',
    description:
      'Official template repository for building Abstract Backend providers. It packages the developer studio workflow, contract tests, and docs so teams can ship new implementations quickly.',
    website: 'https://github.com/Chisanan232/abstract-backend-implementation-template',
    source: 'https://github.com/Chisanan232/abstract-backend-implementation-template',
    tags: ['template', 'developer-studio', 'message-queue', 'starter'],
    isTemplate: true,
  },
  {
    title: 'abe-redis',
    description:
      'Production-ready Redis provider implementing the Abstract Backend queue contracts. Built on the template, it showcases durable streams, consumer groups, and real deployment guidance.',
    website: 'https://github.com/Chisanan232/abe-redis',
    source: 'https://github.com/Chisanan232/abe-redis',
    tags: ['implementation', 'redis', 'message-queue', 'template'],
    badges: [
      {
        href: 'https://github.com/Chisanan232/abe-redis/releases',
        image:
          'https://img.shields.io/github/v/release/Chisanan232/abe-redis?display_name=tag&sort=semver&logo=github',
        alt: 'GitHub release status',
      },
      {
        href: 'https://pypi.org/project/abe-redis/',
        image: 'https://img.shields.io/pypi/v/abe-redis?logo=pypi',
        alt: 'PyPI version',
      },
    ],
  },
];

const TAGS = ['all', 'template', 'implementation', 'redis', 'message-queue', 'mcp'];

export default function Showcase(): JSX.Element {
  const [selectedTag, setSelectedTag] = useState('all');

  const filteredProjects = selectedTag === 'all'
    ? PROJECTS
    : PROJECTS.filter(project => project.tags.includes(selectedTag));

  return (
    <Layout
      title="Showcase"
      description="Examples that build on the Abstract Backend architecture">
      <main className={styles.showcaseMain}>
        <div className={clsx('container', styles.showcaseContainer)}>
          <div className={styles.showcaseHeader}>
            <h1 className={styles.showcaseTitle}>Showcase</h1>
            <p className={styles.showcaseDescription}>
              Explore repositories that apply the Abstract Backend patterns in real projects. The template helps
              teams bootstrap new providers quickly, and the Redis implementation shows a concrete backend in action.
            </p>
          </div>

          <div className={styles.showcaseFilters}>
            <div className={styles.filterButtons}>
              {TAGS.map((tag) => (
                <button
                  key={tag}
                  className={clsx(
                    'button',
                    selectedTag === tag ? 'button--primary' : 'button--outline button--secondary',
                    styles.filterButton
                  )}
                  onClick={() => setSelectedTag(tag)}>
                  {tag === 'all' ? 'All' : tag}
                </button>
              ))}
            </div>
            <div className={styles.showcaseCount}>
              Showing {filteredProjects.length} {filteredProjects.length === 1 ? 'project' : 'projects'}
            </div>
          </div>

          <div className="row">
            {filteredProjects.map((project) => (
              <ShowcaseCard key={project.title} project={project} />
            ))}
          </div>

          <div className={styles.showcaseFooter}>
            <h2>Add Your Project</h2>
            <p>
              Built your own provider or template on top of Abstract Backend? Share it so others can learn from it.
            </p>
            <div className={styles.footerButtons}>
              <a
                className="button button--primary button--lg"
                href="https://github.com/Chisanan232/abstract-backend/issues/new"
                target="_blank"
                rel="noopener noreferrer">
                Submit Your Project
              </a>
              <a
                className="button button--secondary button--lg"
                href="https://github.com/Chisanan232/abstract-backend"
                target="_blank"
                rel="noopener noreferrer">
                View the Abstract Backend Repo
              </a>
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}
