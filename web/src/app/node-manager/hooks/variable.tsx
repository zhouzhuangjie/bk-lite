import { useTranslation } from '@/utils/i18n';
import { Button, Popconfirm, type TableColumnsType } from 'antd';
import type { TableDataItem } from '@/app/node-manager/types/index';
import { VariableProps } from '@/app/node-manager/types/cloudregion';
export const useVarColumns = ({
  openUerModal,
  getFormDataById,
  delconfirm,
}: VariableProps): TableColumnsType<TableDataItem> => {
  const { t } = useTranslation();
  const columns: TableColumnsType<TableDataItem> = [
    {
      title: t('common.name'),
      dataIndex: 'name',
      render: (text: string) => <p>{text}</p>,
    },
    {
      title: t('node-manager.cloudregion.variable.value'),
      dataIndex: 'value',
    },
    {
      title: t('node-manager.cloudregion.variable.desc'),
      dataIndex: 'description',
      render: (text: string) => <p>{text || '--'}</p>,
    },
    {
      title: t('common.actions'),
      dataIndex: 'key',
      fixed: 'right',
      render: (key: string, text) => (
        <div>
          <Button
            onClick={() => {
              openUerModal('edit', getFormDataById(key));
            }}
            color="primary"
            variant="link"
          >
            {t('common.edit')}
          </Button>

          <Popconfirm
            title={t('node-manager.cloudregion.variable.deletevariable')}
            description={t('node-manager.cloudregion.variable.deleteinfo')}
            okText={t('common.confirm')}
            cancelText={t('common.cancel')}
            onConfirm={() => {
              delconfirm(key, text);
            }}
          >
            <Button color="primary" variant="link">
              {t('common.delete')}
            </Button>
          </Popconfirm>
        </div>
      ),
    },
  ];
  return columns;
};
