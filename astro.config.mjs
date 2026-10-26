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
			customCss: ['./src/styles/custom.css'],
			social: [
				{
					icon: 'github',
					label: 'GitHub',
					href: 'https://github.com/Mobile-Consulting-Solutions-Training/training-notes-site',
				},
			],
			sidebar: [
				{
					label: '📓 Notes',
					items: [{ autogenerate: { directory: 'notes' } }],
				},
				{
					label: '🧭 Walkthroughs',
					items: [{ autogenerate: { directory: 'walkthroughs' } }],
				},
				{
					label: '📝 Study Guides',
					items: [{ autogenerate: { directory: 'study-guide' } }],
				},
				{
					label: '🔤 Vocabulary',
					items: [{ autogenerate: { directory: 'vocabulary' } }],
				},
				{ label: '🎬 Videos', slug: 'videos' },
				{
					label: '✅ Homework',
					items: [{ autogenerate: { directory: 'homework' } }],
				},
			],
		}),
	],
});
