// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://mobile-consulting-solutions-training.github.io',
	base: '/training-notes-site',
	// Walkthroughs used to live under notes/; keep old shared links working
	redirects: {
		'/notes/sql-training-walkthrough': '/training-notes-site/walkthroughs/sql-training-walkthrough/',
		'/notes/hive-spark-etl-walkthrough': '/training-notes-site/walkthroughs/hive-spark-etl-walkthrough/',
		'/videos': '/training-notes-site/reference/videos/',
		// Vocabulary sheets used to live under study-guide/
		'/study-guide/day-0-vocabulary': '/training-notes-site/vocabulary/day-0/',
		'/study-guide/day-1-vocabulary': '/training-notes-site/vocabulary/day-1/',
		'/study-guide/day-2-vocabulary': '/training-notes-site/vocabulary/day-2/',
		'/study-guide/day-5-vocabulary': '/training-notes-site/vocabulary/day-5/',
		'/study-guide/combined-vocabulary': '/training-notes-site/vocabulary/combined/',
	},
	integrations: [
		starlight({
			title: 'Big Data Handbook',
			// Per-page "Last updated" from git history (deploy checks out full history)
			lastUpdated: true,
			customCss: ['./src/styles/custom.css'],
			social: [
				{
					icon: 'github',
					label: 'GitHub',
					href: 'https://github.com/Mobile-Consulting-Solutions-Training/training-notes-site',
				},
			],
			sidebar: [
				{ label: "🆕 What's New", slug: 'whats-new' },
				{ label: '🎯 Final Project', slug: 'final-project' },
				{
					label: '📓 Notes',
					items: [{ autogenerate: { directory: 'notes' } }],
					collapsed: true,
				},
				{
					label: '🧭 Walkthroughs',
					items: [{ autogenerate: { directory: 'walkthroughs' } }],
					collapsed: true,
				},
				{
					label: '📝 Study Guides',
					items: [{ autogenerate: { directory: 'study-guide' } }],
					collapsed: true,
				},
				{
					label: '🔤 Vocabulary',
					items: [{ autogenerate: { directory: 'vocabulary' } }],
					collapsed: true,
				},
				{
					label: '🧰 Reference',
					items: [{ autogenerate: { directory: 'reference' } }],
					collapsed: true,
				},
				{
					label: '✅ Homework',
					items: [{ autogenerate: { directory: 'homework' } }],
					collapsed: true,
				},
			],
		}),
	],
});
