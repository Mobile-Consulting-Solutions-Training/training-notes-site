// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://mobile-consulting-solutions-training.github.io',
	base: '/training-notes-site',
	integrations: [
		starlight({
			title: 'MCS Training Notes',
			social: [
				{
					icon: 'github',
					label: 'GitHub',
					href: 'https://github.com/Mobile-Consulting-Solutions-Training/training-notes-site',
				},
			],
			sidebar: [
				{
					label: 'Notes',
					items: [{ autogenerate: { directory: 'notes' } }],
				},
				{
					label: 'Study Guides',
					items: [{ autogenerate: { directory: 'study-guide' } }],
				},
				{
					label: 'Homework',
					items: [{ autogenerate: { directory: 'homework' } }],
				},
			],
		}),
	],
});
