import type { Meta, StoryObj } from '@storybook/react';
import TopMenu from '@/components/top-menu';

const meta: Meta<typeof TopMenu> = {
  component: TopMenu,
};

export default meta;

type Story = StoryObj<typeof TopMenu>;

const mockMenuItems = [
  { label: 'Home', icon: 'home', path: '/' },
  { label: 'About', icon: 'info', path: '/about' },
  { label: 'Contact', icon: 'contact', path: '/contact' },
];

export const Default: Story = {
  args: {
    menuItems: mockMenuItems,
  },
};