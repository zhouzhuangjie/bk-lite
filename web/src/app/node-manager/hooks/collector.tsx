import { ColumnItem } from '@/types';
import { useTranslation } from '@/utils/i18n';
import { useLocalizedTime } from '@/hooks/useLocalizedTime';
import { Button, Popconfirm } from 'antd';
// import Permission from '@/components/permission';

export const useDetailColumns = ({
  handleDelete,
}: {
  handleDelete: (id: number) => void;
}): ColumnItem[] => {
  const { t } = useTranslation();
  const { convertToLocalizedTime } = useLocalizedTime();
  const detailColumns: ColumnItem[] = [
    {
      title: t('node-manager.collector.packageName'),
      dataIndex: 'name',
      key: 'name',
      width: 120,
      ellipsis: true,
      render: (_, record) => <>{record.name || '--'}</>,
    },
    {
      title: t('node-manager.collector.version'),
      dataIndex: 'version',
      key: 'version',
      width: 120,
      ellipsis: true,
      render: (_, record) => <>{record.version || '--'}</>,
    },
    {
      title: t('node-manager.collector.updatedBy'),
      dataIndex: 'updated_by',
      key: 'updated_by',
      width: 120,
      ellipsis: true,
      render: (_, record) => <>{record.updated_by || '--'}</>,
    },
    {
      title: t('node-manager.collector.updatedAt'),
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 120,
      ellipsis: true,
      render: (_, { updated_at }) => <>{updated_at ? convertToLocalizedTime(new Date(updated_at) + '') : '--'}</>,
    },
    {
      title: t('common.actions'),
      key: 'action',
      dataIndex: 'action',
      width: 120,
      fixed: 'right',
      render: (_, { id }) => (
        // <>
        //   <Permission requiredPermissions={['Operate']}>
        //     <Popconfirm
        //       title={t(`node-manager.collector.delete`)}
        //       description={t(`node-manager.collector.deleteInfo`)}
        //       okText={t("common.confirm")}
        //       cancelText={t("common.cancel")}
        //       onConfirm={() => {
        //         deletePackage(record?.id)
        //       }}
        //     >
        //       <Button
        //         type="link"
        //         disabled={record.status !== 'new'}
        //       >
        //         {t('common.delete')}
        //       </Button>
        //     </Popconfirm>
        //   </Permission>
        // </>
        <>
          <Popconfirm
            title={t(`node-manager.collector.delete`)}
            description={t(`node-manager.collector.deleteInfo`)}
            okText={t("common.confirm")}
            cancelText={t("common.cancel")}
            onConfirm={() => handleDelete(id)}
          >
            <Button
              type="link"
            >
              {t('common.delete')}
            </Button>
          </Popconfirm>
        </>
      ),
    },
  ];

  return detailColumns;
} 