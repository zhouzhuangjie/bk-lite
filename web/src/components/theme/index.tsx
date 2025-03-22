'use client';

import { useEffect, useState } from 'react';
import Icon from '@/components/icon';
import { useTheme } from '@/context/theme';
import { useTranslation } from '@/utils/i18n';

const ThemeSwitcher = () => {
  const { t } = useTranslation();
  const { setTheme } = useTheme();
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      setIsDarkMode(true);
    } else {
      setIsDarkMode(false);
    }
  }, []);

  const handleToggle = () => {
    const newTheme = !isDarkMode ? 'dark' : 'light';
    setIsDarkMode(!isDarkMode);
    setTheme(newTheme === 'dark');
    localStorage.setItem('theme', newTheme);
  };

  return (
    <div className="flex w-full justify-between items-center" onClick={handleToggle}>
      {t('common.theme')}
      <span className="text-base text-[var(--color-text-4)]">
        <div className='flex items-center cursor-pointer'>
          {isDarkMode ? <Icon type='anse' /> : <Icon type='liangse' />}
        </div>
      </span>
    </div>
  );
}

export default ThemeSwitcher;
