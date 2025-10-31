import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  icon: string;
  description: string;
  cta: string;
  href: string;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Modular Queue Providers',
    icon: '🛰️',
    description:
      'Swap providers at light-speed. Structural typing, contract tests, and runtime discovery keep every backend aligned with the same orbit.',
    cta: 'Explore provider lifecycle',
    href: '/dev/next/architecture/provider-lifecycle',
  },
  {
    title: 'Observability-First Tooling',
    icon: '🌌',
    description:
      'From logging presets to coverage dashboards, the toolkit surfaces every signal so you can navigate the abstract backend cosmos with clarity.',
    cta: 'See the logging guide',
    href: '/dev/next/logging',
  },
  {
    title: 'Production-Ready Automation',
    icon: '🚀',
    description:
      'Reusable workflows publish packages, docs, and release notes. Intent-driven automation keeps CI/CD synchronized across galaxies.',
    cta: 'Review CI/CD playbook',
    href: '/dev/next/ci-cd/continuous-integration',
  },
];

function Feature({title, icon, description, cta, href}: FeatureItem) {
  return (
    <article className={clsx('col col--4', styles.card)}>
      <div className={styles.cardBackdrop} />
      <div className={styles.cardContent}>
        <span className={styles.cardIcon} aria-hidden="true">
          {icon}
        </span>
        <Heading as="h3" className={styles.cardTitle}>
          {title}
        </Heading>
        <p className={styles.cardCopy}>{description}</p>
        <Link className={styles.cardLink} to={href}>
          {cta}
        </Link>
      </div>
    </article>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className={styles.featuresInner}>
        <div className="row">
          {FeatureList.map((feature) => (
            <Feature key={feature.title} {...feature} />
          ))}
        </div>
      </div>
    </section>
  );
}
