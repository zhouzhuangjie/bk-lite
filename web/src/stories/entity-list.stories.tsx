import React from 'react';
import { StoryFn, Meta } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import { Menu } from 'antd';
import EntityList from '@/components/entity-list';

interface ExampleItem {
  id: string;
  name: string;
  description: string;
  icon: string;
  avatar?: string;
  tag?: string[];
}

const Template: StoryFn<any> = (args) => <EntityList {...args} />;

export default {
  title: 'Components/EntityList',
  component: EntityList,
} as Meta;

const exampleData: ExampleItem[] = [
  {
    id: '1',
    name: 'Entity One',
    description: 'Description of entity one.',
    icon: 'icon1',
    tag: ['tag1', 'tag2'],
  },
  {
    id: '2',
    name: 'Entity Two',
    description: 'Description of entity two.',
    icon: 'icon2',
    tag: ['tag3'],
  },
  {
    id: '3',
    name: 'Entity Three',
    description: 'Description of entity three.',
    icon: 'icon3',
    tag: ['tag4', 'tag5'],
  },
];

export const Default = Template.bind({});
Default.args = {
  data: exampleData,
  loading: false,
  onSearch: (value: string) => action('onSearch')(value),
  openModal: () => action('openModal')(),
};

export const WithSearch = Template.bind({});
WithSearch.args = {
  data: exampleData,
  loading: false,
  onSearch: (value: string) => action('onSearch')(value),
};

export const Loading = Template.bind({});
Loading.args = {
  data: [],
  loading: true,
};

export const WithMenuActions = Template.bind({});
WithMenuActions.args = {
  data: exampleData,
  loading: false,
  onSearch: (value: string) => action('onSearch')(value),
  menuActions: (item: ExampleItem) => (
    <Menu>
      <Menu.Item key="edit" onClick={() => action('edit')(item)}>Edit</Menu.Item>
      <Menu.Item key="delete" onClick={() => action('delete')(item)}>Delete</Menu.Item>
    </Menu>
  ),
  onCardClick: (item: ExampleItem) => action('cardClick')(item),
};

export const WithAddNewButton = Template.bind({});
WithAddNewButton.args = {
  data: exampleData,
  loading: false,
  openModal: () => action('openModal')(),
};

export const WithTagBelowName = Template.bind({});
WithTagBelowName.args = {
  data: exampleData,
  loading: false,
  onSearch: (value: string) => action('onSearch')(value),
  displayTagBelowName: true,
};

export const WithMultipleActions = Template.bind({});
WithMultipleActions.args = {
  data: exampleData,
  loading: false,
  menuActions: (item: ExampleItem) => (
    <Menu>
      <Menu.Item key="edit" onClick={() => action('edit')(item)}>Edit</Menu.Item>
      <Menu.Item key="delete" onClick={() => action('delete')(item)}>Delete</Menu.Item>
    </Menu>
  ),
  singleAction: (item: ExampleItem) => ({
    text: 'Action Button',
    onClick: () => action('buttonClick')(item),
  }),
  openModal: () => action('openModal')(),
  displayTagBelowName: true,
};

export const Empty = Template.bind({});
Empty.args = {
  data: [],
  loading: false,
  onSearch: (value: string) => action('onSearch')(value),
};
