'use client';
import React, {
  useEffect,
  useRef,
  useState,
  useMemo,
  useCallback,
} from 'react';
import { Button, Input, message, Space, Modal, Tooltip, Tag } from 'antd';
import { DownOutlined, ReloadOutlined } from '@ant-design/icons';
import type { MenuProps, TableProps } from 'antd';
import nodeStyle from './index.module.scss';
import { Dropdown, Segmented } from 'antd';
import CollectorModal from './collectorModal';
import { useTranslation } from '@/utils/i18n';
import type { GetProps } from 'antd';
import { ModalRef, TableDataItem } from '@/app/node-manager/types/index';
import CustomTable from '@/components/custom-table/index';
import { useColumns } from '@/app/node-manager/hooks/node';
import Mainlayout from '../mainlayout/layout';
import useApiClient from '@/utils/request';
import useApiCloudRegion from '@/app/node-manager/api/cloudregion';
import useCloudId from '@/app/node-manager/hooks/useCloudid';
import { useTelegrafMap } from '@/app/node-manager/constants/cloudregion';
import ControllerInstall from './controllerInstall';
import ControllerUninstall from './controllerUninstall';
import CollectorInstallTable from './controllerTable';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  OPERATE_SYSTEMS,
  useSidecaritems,
  useCollectoritems,
} from '@/app/node-manager/constants/cloudregion';
import { cloneDeep } from 'lodash';
const { confirm } = Modal;
const { Search } = Input;

type TableRowSelection<T extends object = object> =
  TableProps<T>['rowSelection'];
type SearchProps = GetProps<typeof Input.Search>;

const Node = () => {
  const collectorRef = useRef<ModalRef>(null);
  const controllerRef = useRef<ModalRef>(null);
  const { t } = useTranslation();
  const cloudId = useCloudId();
  const searchParams = useSearchParams();
  const name = searchParams.get('name') || '';
  const { isLoading, del } = useApiClient();
  const { getnodelist } = useApiCloudRegion();
  const [nodelist, setNodelist] = useState<TableDataItem[]>();
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [showNodeTable, setShowNodeTable] = useState<boolean>(true);
  const [searchText, setSearchText] = useState<string>('');
  const [taskId, setTaskId] = useState<string>('');
  const [tableType, setTableType] = useState<string>('');
  const [showInstallController, setShowInstallController] =
    useState<boolean>(false);
  const [showInstallCollectorTable, setShowInstallCollectorTable] =
    useState<boolean>(false);
  const [system, setSystem] = useState<string>('linux');
  const router = useRouter();
  const checkConfig = (row: TableDataItem) => {
    const data = {
      cloud_region_id: cloudId,
      name,
      id: row.id + '',
    };
    const params = new URLSearchParams(data);
    const targetUrl = `/node-manager/cloudregion/configuration?${params.toString()}`;
    router.push(targetUrl);
  };
  const columns = useColumns({ checkConfig });
  const sidecaritems = useSidecaritems();
  const collectoritems = useCollectoritems();
  const statusMap = useTelegrafMap();

  const cancelInstall = useCallback(() => {
    setShowNodeTable(true);
    setShowInstallController(false);
  }, []);

  const cancelWait = useCallback(() => {
    setShowNodeTable(true);
    setShowInstallCollectorTable(false);
  }, []);

  const getCollectors = (collectors: TableDataItem) => {
    const seenIds = new Set(); // 用于存储已经出现过的 id
    const data = collectors.filter((item: TableDataItem) => {
      if (!seenIds.has(item.id)) {
        seenIds.add(item.id); // 如果 id 没有出现过，添加到集合中
        return true; // 保留这个元素
      }
      return false; // 如果 id 已经出现过，过滤掉这个元素
    });
    return data.map((tex: TableDataItem) => {
      if (tex.configuration_name === 'Nats Executor') {
        return {
          title: tex.configuration_name,
          dataIndex: tex.configuration_name,
          render: (key: string, item: TableDataItem) => {
            const target = (item.status.collectors || []).find(
              (item: TableDataItem) =>
                item.configuration_name === tex.configuration_name
            );
            return (
              <Tooltip title={`${target?.message}`}>
                <Tag
                  bordered={false}
                  color={!target?.status ? 'success' : 'error'}
                >
                  {!item.status?.status ? 'Running' : 'Error'}
                </Tag>
              </Tooltip>
            );
          },
        };
      }
      return {
        title: tex.collector_name,
        dataIndex: tex.collector_id,
        render: (key: string, item: TableDataItem) => {
          const target = (item.status.collectors || []).find(
            (item: TableDataItem) => item.collector_id === tex.collector_id
          );
          return (
            <div>
              <span
                className="recordStatus"
                style={{
                  backgroundColor:
                    statusMap[target?.status]?.color || '#b2b5bd',
                }}
              ></span>
              <span
                style={{ color: statusMap[target?.status]?.color || '#b2b5bd' }}
              >
                {target?.message || '--'}
              </span>
            </div>
          );
        },
      };
    });
  };

  const enableOperateSideCar = useMemo(() => {
    if (!selectedRowKeys.length) return true;
    const list = (nodelist || []).filter((item) =>
      selectedRowKeys.includes(item.key)
    );
    return list.some((item) => item.status?.status !== 0);
  }, [selectedRowKeys, nodelist]);

  const tableColumns = useMemo(() => {
    if (!nodelist?.length) return columns;
    const activeColumns = cloneDeep(columns);
    const collectors = getCollectors(
      nodelist.reduce((pre, cur) => {
        return pre.concat(cur.status?.collectors || []);
      }, [])
    );
    activeColumns.splice(2, 0, ...collectors);
    return activeColumns;
  }, [columns, nodelist, statusMap]);

  const enableOperateCollecter = useMemo(() => {
    if (!selectedRowKeys.length) return true;
    const list = (nodelist || []).filter((item) =>
      selectedRowKeys.includes(item.key)
    );
    return list.some((item) => item.status?.status !== 0);
  }, [selectedRowKeys, nodelist]);

  useEffect(() => {
    if (!isLoading) {
      getNodes();
    }
  }, [isLoading]);

  const handleSidecarMenuClick: MenuProps['onClick'] = (e) => {
    if (e.key === 'uninstallSidecar') {
      const list = (nodelist || []).filter((item) =>
        selectedRowKeys.includes(item.key)
      );
      controllerRef.current?.showModal({
        type: e.key,
        form: { list },
      });
      return;
    }
    confirm({
      title: t('common.prompt'),
      content: t(`node-manager.cloudregion.node.${e.key}Tips`),
      centered: true,
      onOk() {
        return new Promise(async (resolve) => {
          const params = JSON.stringify(selectedRowKeys);
          try {
            await del(`/monitor/api/monitor_policy/${params}/`);
            message.success(t('common.operationSuccessful'));
            getNodes();
          } finally {
            resolve(true);
          }
        });
      },
    });
  };

  const handleCollectorMenuClick: MenuProps['onClick'] = (e) => {
    collectorRef.current?.showModal({
      type: e.key,
      ids: selectedRowKeys as string[],
      selectedsystem: system,
    });
  };

  const SidecarmenuProps = {
    items: sidecaritems,
    onClick: handleSidecarMenuClick,
  };

  const CollectormenuProps = {
    items: collectoritems,
    onClick: handleCollectorMenuClick,
  };

  //选择相同的系统节点，判断是否禁用按钮
  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    setSelectedRowKeys(newSelectedRowKeys);
  };

  const getCheckboxProps = () => {
    return {
      disabled: false,
    };
  };

  const rowSelection: TableRowSelection<TableDataItem> = {
    selectedRowKeys,
    onChange: onSelectChange,
    getCheckboxProps: getCheckboxProps,
  };

  const onSearch: SearchProps['onSearch'] = (value) => {
    setSearchText(value);
    const params = getParams();
    params.name = value;
    getNodes(params);
  };

  const getParams = () => {
    return {
      name: searchText,
      operating_system: system,
      cloud_region_id: Number(cloudId),
    };
  };

  const getNodes = async (params?: {
    name?: string;
    operating_system?: string;
    cloud_region_id?: number;
  }) => {
    setLoading(true);
    const res = await getnodelist(params || getParams());
    const data = res.map((item: TableDataItem) => ({
      ...item,
      key: item.id,
    }));
    setLoading(false);
    setNodelist(data);
  };

  const handleInstallController = () => {
    setShowNodeTable(false);
    setShowInstallController(true);
  };

  const onSystemChange = (id: string) => {
    setSystem(id);
    const params = getParams();
    params.operating_system = id;
    getNodes(params);
  };

  const handleCollector = (config = { type: '', taskId: '' }) => {
    getNodes();
    if (['installCollector', 'uninstallController'].includes(config.type)) {
      setTaskId(config.taskId);
      setTableType(
        config.type.includes('Collector') ? 'collector' : 'controller'
      );
      setShowNodeTable(false);
      setShowInstallCollectorTable(true);
    }
  };

  return (
    <Mainlayout>
      {showNodeTable && (
        <div className={`${nodeStyle.node} w-full h-full`}>
          <div className="overflow-hidden">
            <div className="flex justify-between w-full overflow-y-hidden mb-4">
              <Segmented
                options={OPERATE_SYSTEMS}
                value={system}
                onChange={onSystemChange}
              />
              <div>
                <Search
                  className="w-64 mr-[8px]"
                  placeholder={t('common.search')}
                  enterButton
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onSearch={onSearch}
                />
                <ReloadOutlined
                  className="mr-[8px]"
                  onClick={() => getNodes()}
                />
                <Button
                  type="primary"
                  className="mr-[8px]"
                  onClick={handleInstallController}
                >
                  {t('node-manager.cloudregion.node.installController')}
                </Button>
                <Dropdown
                  className="mr-[8px]"
                  menu={SidecarmenuProps}
                  disabled={enableOperateSideCar}
                >
                  <Button>
                    <Space>
                      {t('node-manager.cloudregion.node.sidecar')}
                      <DownOutlined />
                    </Space>
                  </Button>
                </Dropdown>
                <Dropdown
                  className="mr-[8px]"
                  menu={CollectormenuProps}
                  disabled={enableOperateCollecter}
                >
                  <Button>
                    <Space>
                      {t('node-manager.cloudregion.node.collector')}
                      <DownOutlined />
                    </Space>
                  </Button>
                </Dropdown>
              </div>
            </div>
            <div className="tablewidth">
              <CustomTable
                columns={tableColumns}
                loading={loading}
                dataSource={nodelist}
                scroll={{ y: 'calc(100vh - 400px)', x: 'calc(100vw - 300px)' }}
                rowSelection={rowSelection}
              />
            </div>
            <CollectorModal
              ref={collectorRef}
              onSuccess={(config) => {
                handleCollector(config);
              }}
            />
            <ControllerUninstall
              ref={controllerRef}
              config={{ os: system }}
              onSuccess={(config) => {
                handleCollector(config);
              }}
            />
          </div>
        </div>
      )}
      {showInstallController && (
        <ControllerInstall config={{ os: system }} cancel={cancelInstall} />
      )}
      {showInstallCollectorTable && (
        <CollectorInstallTable
          config={{ taskId, type: tableType }}
          cancel={cancelWait}
        />
      )}
    </Mainlayout>
  );
};

export default Node;
