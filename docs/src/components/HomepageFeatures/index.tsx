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
    title: 'Entry-Point Powered Providers',
    icon: '🚀',
    description:
      'Activate or retire providers in seconds using Python entry points—`pip install` turns them on, `pip uninstall` turns them off—without touching application code.',
    cta: 'Switch providers instantly',
    href: '/docs/next/quick-start/requirements',
  },
  {
    title: 'Crystal-Clear Abstractions',
    icon: '🧭',
    description:
      'A lightweight contract models every backend component. Follow the protocol to add implementations, or deprecate them cleanly, while the rest of your stack stays unchanged.',
    cta: 'Understand the architecture',
    href: '/dev/next/architecture/project-structure',
  },
  {
    title: 'Modular Queue Providers',
    icon: '🛰️',
    description:
      'First-class message queue definitions ship with contract tests, payload typing, and lifecycle docs so you can lean on queues—the backbone of modern backend systems.',
    cta: 'Explore provider lifecycle',
    href: '/dev/next/architecture/provider-lifecycle',
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
