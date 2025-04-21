'use client';
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Input, Button, message } from 'antd';
import type { GetProps } from 'antd';
import { ColumnFilterItem } from 'antd/es/table/interface';
import { useRouter, useSearchParams } from 'next/navigation';
import CustomTable from '@/components/custom-table';
import { ModalRef, TableDataItem } from '@/app/node-manager/types/index';
import { useTranslation } from '@/utils/i18n';
import useApiClient from '@/utils/request';
import type {
  IConfiglistprops,
  ConfigDate,
  SubRef,
} from '@/app/node-manager/types/cloudregion';
import useApiCloudRegion from '@/app/node-manager/api/cloudregion';
import useApiCollector from '@/app/node-manager/api/collector';
import useCloudId from '@/app/node-manager/hooks/useCloudid';
import Mainlayout from '../mainlayout/layout';
import configstyle from './index.module.scss';
import SubConfiguration from './subconfiguration';
import { useConfigColumns } from '@/app/node-manager/hooks/configuration';
import ConfigModal from './configModal';
type SearchProps = GetProps<typeof Input.Search>;
const { Search } = Input;

const Configration = () => {
  const subConfiguration = useRef<SubRef>(null);
  const configurationRef = useRef<ModalRef>(null);
  const cloudid = useCloudId();
  const router = useRouter();
  const { t } = useTranslation();
  const { isLoading } = useApiClient();
  const searchParams = useSearchParams();
  const nodeId = JSON.parse(
    sessionStorage.getItem('cloudRegionInfo') || '{}'
  ).id;
  const cloudregionId = searchParams.get('cloud_region_id') || '';
  const name = searchParams.get('name') || '';
  const { getconfiglist, getnodelist, batchdeletecollector } =
    useApiCloudRegion();
  const { getCollectorlist } = useApiCollector();
  const [loading, setLoading] = useState<boolean>(true);
  const [configData, setConfigData] = useState<ConfigDate[]>([]);
  const [showSub, setShowSub] = useState<boolean>(false);
  const [filters, setFilters] = useState<ColumnFilterItem[]>([]);
  const [nodeData, setNodeData] = useState<ConfigDate>({
    key: '',
    name: '',
    collector: '',
    operatingsystem: '',
    nodecount: 0,
    configinfo: '',
    nodes: [],
  });
  const [collectorIds, setCollectorIds] = useState<string[]>([]);
  const [originNodes, setOriginNodes] = useState<TableDataItem[]>([]);
  const [originConfigs, setOriginConfigs] = useState<IConfiglistprops[]>([]);
  const [originCollectors, setOriginCollectors] = useState<TableDataItem[]>([]);

  const showConfigurationModal = (type: string, form: any) => {
    configurationRef.current?.showModal({
      type,
      form,
    });
  };

  //点击编辑配置文件的触发事件
  const configurationClick = (key: string) => {
    const configurationformdata = configData.find((item) => item.key === key);
    showConfigurationModal('edit', configurationformdata);
  };

  // 子配置编辑触发弹窗事件
  const hanldeSubEditClick = (item: any) => {
    showConfigurationModal('edit_child', item);
  };

  const openSub = (key: string, item?: any) => {
    if (item) {
      setNodeData({
        ...item,
        nodesList: originNodes.map((item) => ({
          label: item?.ip,
          value: item?.id,
        })),
      });
    }
    setShowSub(true);
  };

  const nodeClick = () => {
    router.push(
      `/node-manager/cloudregion/node?cloudregion_id=${cloudregionId}&name=${name}`
    );
  };

  //批量删除的确定的弹窗
  const modifydeleteconfirm = async (id: string) => {
    setLoading(true);
    await batchdeletecollector({
      ids: [id],
    });
    message.success(t('common.deleteSuccess'));
    getConfigData();
  };

  const { columns } = useConfigColumns({
    configurationClick,
    filter: filters,
    openSub,
    nodeClick,
    modifydeleteconfirm,
  });

  useEffect(() => {
    if (isLoading) return;
    initPage();
    return () => {
      sessionStorage.removeItem('cloudRegionInfo');
    };
  }, [isLoading]);

  const tableData = useMemo(() => {
    if (!collectorIds.length) return configData;
    if (configData.length && collectorIds.length) {
      return configData.filter((item) => {
        return collectorIds.includes(item.collector);
      });
    }
    return [];
  }, [collectorIds, configData]);

  //获取配置文件列表
  const initPage = async () => {
    setLoading(true);
    try {
      const res = await Promise.all([
        getconfiglist(Number(cloudid), nodeId || ''),
        getnodelist({ cloud_region_id: Number(cloudid) }),
        getCollectorlist({}),
      ]);
      const configlist = res[0] || [];
      const nodeList = res[1] || [];
      setFilterConfig(res[2] || []);
      setOriginConfigs(configlist);
      setOriginNodes(nodeList);
      dealConfigData({
        configlist,
        nodeList,
      });
    } finally {
      setLoading(false);
    }
  };

  const dealConfigData = (
    config = {
      configlist: originConfigs,
      nodeList: originNodes,
    }
  ) => {
    const nodes = config.nodeList.map((item) => ({
      label: item?.ip,
      value: item?.id,
    }));
    const data: any = config.configlist.map((item: IConfiglistprops) => {
      return {
        ...item,
        key: item.id,
        operatingsystem: item.operating_system,
        nodecount: item.node_count,
        configinfo: item.config_template,
        nodesList: nodes || [],
      };
    });
    setConfigData(data);
  };

  const getConfigData = async (search = '') => {
    setLoading(true);
    try {
      const data = await getconfiglist(Number(cloudid), search || '');
      dealConfigData({
        configlist: data,
        nodeList: originNodes,
      });
    } finally {
      setLoading(false);
    }
  };

  // 根据采集器列表过滤数据
  const setFilterConfig = (data: TableDataItem[]) => {
    const collectors = data.filter((item: any) => !item.controller_default_run);
    setOriginCollectors(collectors);
    const filters = new Map();
    const collectorIds = collectors.map((item: any) => {
      filters.set(item.name, { text: item.name, value: item.name });
      return item.id;
    });
    setFilters(Array.from(filters.values()) as ColumnFilterItem[]);
    setCollectorIds(collectorIds);
  };

  //搜索框的触发事件
  const onSearch: SearchProps['onSearch'] = (value) => {
    getConfigData(value);
  };

  // 子配置返回配置页面事件
  const handleCBack = () => {
    getConfigData();
    setShowSub(false);
  };

  // 弹窗确认成功后的回调
  const onSuccess = () => {
    if (!showSub) {
      getConfigData();
      return;
    }
    subConfiguration.current?.getChildConfig();
  };

  return (
    <Mainlayout>
      <div className={`${configstyle.config} w-full h-full`}>
        {!showSub ? (
          <>
            <div className="flex justify-end mb-4">
              <Button
                className="mr-[8px]"
                type="primary"
                onClick={() => showConfigurationModal('add', {})}
              >
                + {t('common.add')}
              </Button>
              <Search
                className="w-64 mr-[8px]"
                placeholder={t('common.search')}
                enterButton
                onSearch={onSearch}
              />
            </div>
            <div className="tablewidth">
              <CustomTable<any>
                loading={loading}
                scroll={{ y: 'calc(100vh - 400px)', x: 'max-content' }}
                columns={columns}
                dataSource={tableData}
              />
            </div>
          </>
        ) : (
          <SubConfiguration
            ref={subConfiguration}
            collectors={originCollectors}
            cancel={() => handleCBack()}
            edit={hanldeSubEditClick}
            nodeData={nodeData}
          />
        )}
        {/* 弹窗组件（添加，编辑，应用）用于刷新页面 */}
        <ConfigModal
          ref={configurationRef}
          config={{ collectors: originCollectors }}
          onSuccess={onSuccess}
        ></ConfigModal>
      </div>
    </Mainlayout>
  );
};

export default Configration;
