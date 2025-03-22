import { ThemeConfig } from 'antd/es/config-provider/context';
import { theme } from 'antd';

const lightTheme: ThemeConfig = {
  cssVar: true,
  token: {
    colorPrimary: '#155AEF',
  },
  algorithm: theme.defaultAlgorithm,
};

const darkTheme: ThemeConfig = {
  cssVar: true,
  token: {
    colorPrimary: '#155AEF',
  },
  algorithm: theme.darkAlgorithm,
};

export { lightTheme, darkTheme }