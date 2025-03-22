import type { Meta, StoryObj } from '@storybook/react';

import Icon from '@/components/icon';

const meta: Meta<typeof Icon> = {
  component: Icon,
};

export default meta;

type Story = StoryObj<typeof Icon>;

export const Default: Story = {
  args: {
    type: 'jiqiren2',
  },
};
