import type { Meta, StoryObj } from '@storybook/react';

import UserInfo from '@/components/user-info';

const meta: Meta<typeof UserInfo> = {
  component: UserInfo,
};

export default meta;

type Story = StoryObj<typeof UserInfo>;

export const Default: Story = {};
