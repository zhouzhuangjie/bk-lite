import { useTranslation } from '@/utils/i18n';
import { Button, Tag } from 'antd';
import type { TableColumnsType } from 'antd';
import { ConfigHookParams, SubConfigHookParams } from '@/app/node-manager/types/cloudregion';
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
              <Button type="link" onClick={() => { }}>
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
  filter
}: ConfigHookParams) => {
  const { t } = useTranslation();
  const columns: TableColumnsType<TableDataItem> = [
    {
      title: t('common.name'),
      dataIndex: 'name',
      fixed: 'left',
      width: 300,
      render: (text: string) => <p>{text}</p>,
    },
    {
      title: t('node-manager.cloudregion.node.node'),
      dataIndex: 'nodes',
      width: 150,
      render: (text: string) => <p>{text}</p>,
    },
    {
      title: t('node-manager.cloudregion.Configuration.sidecar'),
      dataIndex: 'collector',
      align: 'center',
      filters: filter.map((item) => ({ text: item, value: item })),
      width: 150,
      onFilter: (value, record) => record?.collector === value,
      render: (text: string) => <p>{text}</p>,
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
  edit
}: SubConfigHookParams) => {
  const { t } = useTranslation();
  const columns: TableColumnsType<TableDataItem> = [
    {
      title: t('common.name'),
      dataIndex: 'name',
      fixed: 'left',
      className: 'text-center',
      align: 'center',
      width: 300,
      render: (_: any, record: any) => {
        return (
          <span>{record.name || '--'}</span>
        )
      }
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
              console.log(record);
              edit({
                ...record,
                nodes: nodeData.nodes || '--',
                collector: nodeData.collector,
                configinfo: record.content
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
    columns
  }
}

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
