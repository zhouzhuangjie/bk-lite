import { useMemo } from 'react';
import { ListItem } from '@/types/index';
import { useTranslation } from '@/utils/i18n';

export const useFrequencyList = (): ListItem[] => {
  const { t } = useTranslation();
  return useMemo(
    () => [
      { label: t('common.timeSelector.off'), value: 0 },
      { label: '1m', value: 60000 },
      { label: '5m', value: 300000 },
      { label: '10m', value: 600000 },
    ],
    [t]
  );
};

export  const useTimeRangeList = (): ListItem[] => {
  const { t } = useTranslation();
  return useMemo(
    () => [
      { label: t('common.timeSelector.15Minutes'), value: 15 },
      { label: t('common.timeSelector.30Minutes'), value: 30 },
      { label: t('common.timeSelector.1Hour'), value: 60 },
      { label: t('common.timeSelector.6Hours'), value: 360 },
      { label: t('common.timeSelector.12Hours'), value: 720 },
      { label: t('common.timeSelector.1Day'), value: 1440 },
      { label: t('common.timeSelector.7Days'), value: 10080 },
      { label: t('common.timeSelector.30Days'), value: 43200 },
      { label: t('common.timeSelector.custom'), value: 0 },
    ],
    [t]
  );
};
