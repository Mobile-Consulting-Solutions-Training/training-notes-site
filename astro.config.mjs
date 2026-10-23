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
					label: '✅ Homework',
					items: [{ autogenerate: { directory: 'homework' } }],
				},
			],
		}),
	],
});
