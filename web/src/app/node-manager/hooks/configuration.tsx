import { useTranslation } from '@/utils/i18n';
import { Button, Tag, Popconfirm } from 'antd';
import type { TableColumnsType } from 'antd';
import {
  ConfigHookParams,
  SubConfigHookParams,
} from '@/app/node-manager/types/cloudregion';
import { TableDataItem } from '@/app/node-manager/types/index';

export const useApplyColumns = ({
  handleApply,
  nodes,
}: {
  handleApply: (key: string) => void;
  nodes: string[];
}): TableColumnsType => {
  const { t } = useTranslation();
  //数据
  const applycolumns: TableColumnsType = [
    {
      title: t('node-manager.cloudregion.Configuration.ip'),
      dataIndex: 'ip',
    },
    {
      title: t('node-manager.cloudregion.Configuration.system'),
      dataIndex: 'operatingsystem',
    },
    {
      title: t('node-manager.cloudregion.Configuration.sidecar'),
      dataIndex: 'sidecar',
      className: 'table-cell-center',
      render: (key: string) => {
        if (key === 'Running') {
          return (
            <Tag bordered={false} color="success">
              {key}
            </Tag>
          );
        }
        return (
          <Tag bordered={false} color="error">
            {key}
          </Tag>
        );
      },
    },
    {
      title: t('common.actions'),
      dataIndex: 'key',
      fixed: 'right',
      render: (key: string, sidecarinfo) => {
        return (
          <div>
            {nodes.includes(sidecarinfo.key) ? (
              <Button type="link" onClick={() => {}}>
                {t('common.unapply')}
              </Button>
            ) : (
              <Button
                disabled={sidecarinfo.sidecar != 'Running'}
                type="link"
                onClick={() => {
                  handleApply(key);
                }}
              >
                {t('common.apply')}
              </Button>
            )}
          </div>
        );
      },
    },
  ];
  return applycolumns;
};

export const useConfigColumns = ({
  configurationClick,
  openSub,
  nodeClick,
  modifydeleteconfirm,
  filter,
}: ConfigHookParams) => {
  const { t } = useTranslation();
  const columns: TableColumnsType<TableDataItem> = [
    {
      title: t('common.name'),
      dataIndex: 'name',
      fixed: 'left',
      width: 300,
    },
    {
      title: t('node-manager.cloudregion.node.node'),
      dataIndex: 'nodes',
      width: 150,
      render: (_, record) => {
        return (
          <>
            {record.nodes?.length ? (
              <Button
                type="link"
                className="text-blue-500 hover:text-blue-700"
                onClick={() => nodeClick()}
              >
                {record.nodesList
                  .filter((item: TableDataItem) =>
                    record.nodes.includes(item.value)
                  )
                  .map((item: TableDataItem) => item.label)
                  .join(',')}
              </Button>
            ) : (
              '--'
            )}
          </>
        );
      },
    },
    {
      title: t('node-manager.cloudregion.node.system'),
      dataIndex: 'operatingsystem',
      width: 150,
      render: (_, record) =>
        t(`node-manager.cloudregion.Configuration.${record.operatingsystem}`),
    },
    {
      title: t('node-manager.cloudregion.Configuration.sidecar'),
      dataIndex: 'collector_name',
      align: 'center',
      filters: filter,
      width: 150,
      onFilter: (value, record) => {
        return record?.collector_name === value;
      },
    },
    {
      title: t('common.actions'),
      dataIndex: 'key',
      fixed: 'right',
      align: 'center',
      width: 180,
      render: (key, item) => (
        <div className="flex justify-center">
          <Button
            color="primary"
            variant="link"
            onClick={() => {
              configurationClick(key);
            }}
          >
            {t('common.edit')}
          </Button>
          <Button
            color="primary"
            variant="link"
            onClick={() => {
              openSub(key, item);
            }}
          >
            {t('node-manager.cloudregion.Configuration.subconfiguration')}
          </Button>
          <Popconfirm
            title={t('common.prompt')}
            description={t(
              'node-manager.cloudregion.Configuration.modifydelinfo'
            )}
            okText={t('common.confirm')}
            cancelText={t('common.cancel')}
            onConfirm={() => modifydeleteconfirm(item.key)}
          >
            <Button variant="link" color="primary">
              {t('common.delete')}
            </Button>
          </Popconfirm>
        </div>
      ),
    },
  ];

  return {
    columns,
  };
};

export const useSubConfigColumns = ({
  nodeData,
  edit,
}: SubConfigHookParams) => {
  const { t } = useTranslation();
  const columns: TableColumnsType<TableDataItem> = [
    {
      title: t('node-manager.cloudregion.Configuration.collectionType'),
      dataIndex: 'collect_type',
    },
    {
      title: t('node-manager.cloudregion.Configuration.configurationType'),
      dataIndex: 'config_type',
    },
    {
      title: t('common.actions'),
      dataIndex: 'key',
      fixed: 'right',
      align: 'center',
      width: 180,
      render: (_: any, record: any) => (
        <div className="flex justify-center">
          <Button
            color="primary"
            variant="link"
            onClick={() => {
              edit({
                ...record,
                nodes: nodeData.nodes || [],
                collector: nodeData.collector,
                nodesList: nodeData.nodesList,
                configinfo: record.content,
                operating_system: nodeData.operating_system,
              });
            }}
          >
            {t('common.edit')}
          </Button>
        </div>
      ),
    },
  ];

  return {
    columns,
  };
};

export const useConfigModalColumns = () => {
  const { t } = useTranslation();
  return [
    {
      title: t('node-manager.cloudregion.Configuration.variable'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('node-manager.cloudregion.Configuration.description'),
      dataIndex: 'description',
      key: 'description',
    },
  ];
};
