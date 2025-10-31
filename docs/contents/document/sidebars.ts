import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Sidebar for the Docs section
 */
const sidebars: SidebarsConfig = {
  docs: [
    {
      type: 'doc',
      id: 'introduction',
      label: '📖 Introduction',
    },
    {
      type: 'category',
      label: '🤟 Quickly Start',
      collapsed: false,
      items: [
        {
          type: 'doc',
          id: 'quick-start/quick-start',
          label: '⚡ Quick Start',
        },
        {
          type: 'doc',
          id: 'quick-start/requirements',
          label: '📋 Requirements',
        },
        {
          type: 'doc',
          id: 'quick-start/installation',
          label: '💾 Installation',
        },
        {
          type: 'doc',
          id: 'quick-start/how-to-run',
          label: '▶️ How to Run',
        },
      ],
    },
    {
      type: 'category',
      label: '🧑‍💻 API References',
      items: [
        {
          type: 'doc',
          id: 'api-references/api-references',
          label: '📚 API References',
        },
        {
          type: 'doc',
          id: 'api-references/queue-backend',
          label: '🧱 QueueBackend Protocol',
        },
        {
          type: 'doc',
          id: 'api-references/event-consumer',
          label: '🔁 EventConsumer & AsyncLoopConsumer',
        },
        {
          type: 'doc',
          id: 'api-references/loader',
          label: '🔍 Loader & Discovery',
        },
        {
          type: 'doc',
          id: 'api-references/types',
          label: '🧾 Shared Types',
        },
        {
          type: 'doc',
          id: 'api-references/memory-backend',
          label: '🧠 Memory Backend',
        },
        {
          type: 'doc',
          id: 'api-references/logging',
          label: '🪵 Logging Utilities',
        },
      ],
    },
    {
      type: 'category',
      label: '👋 Welcome to contribute',
      items: [
        {
          type: 'doc',
          id: 'contribute/contribute',
          label: '🤝 Contribute',
        },
        {
          type: 'doc',
          id: 'contribute/report-bug',
          label: '🐛 Report Bug',
        },
        {
          type: 'doc',
          id: 'contribute/request-changes',
          label: '💡 Request Changes',
        },
        {
          type: 'doc',
          id: 'contribute/discuss',
          label: '💬 Discuss',
        },
      ],
    },
    {
      type: 'doc',
      id: 'changelog',
      label: '📝 Changelog',
    },
  ],
};

export default sidebars;
