import type { Meta, StoryObj } from '@storybook/react';

import Spin from '@/components/spin';

const meta: Meta<typeof Spin> = {
  component: Spin,
};

export default meta;

type Story = StoryObj<typeof Spin>;

export const Default: Story = {
  args: {
  },
};
