'use client';
import React, { useEffect, useRef, useState } from 'react';
import { Input } from 'antd';
import type { GetProps } from 'antd';
import { ColumnFilterItem } from 'antd/es/table/interface';
import { useRouter, useSearchParams } from 'next/navigation';
import CustomTable from '@/components/custom-table';
import { ModalRef } from '@/app/node-manager/types/index';
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
  const { getconfiglist, getnodelist } = useApiCloudRegion();
  const { getCollectorlist } = useApiCollector();
  const [loading, setLoading] = useState<boolean>(true);
  const [configdata, setConfigdata] = useState<ConfigDate[]>([]);
  const [tableData, setTableData] = useState<ConfigDate[]>([]);
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
  const [collectorId, setCollectorId] = useState<string[]>([]);

  const showConfigurationModal = (type: string, form: any) => {
    configurationRef.current?.showModal({
      type,
      form,
    })
  };

  //点击编辑配置文件的触发事件
  const configurationClick = (key: string) => {
    const configurationformdata = configdata.find((item) => item.key === key);
    showConfigurationModal('edit', configurationformdata);
  };

  // 子配置编辑触发弹窗事件
  const hanldeSubEditClick = (item: any) => {
    showConfigurationModal('edit_child', item);
  };

  const openSub = (key: string, item?: any) => {
    setNodeData(item);
    setShowSub(true);
  };

  const nodeClick = () => {
    router.push(`/node-manager/cloudregion/node?cloudregion_id=${cloudregionId}&name=${name}`);
  };

  const { columns } = useConfigColumns({
    configurationClick,
    filter: filters,
    openSub,
    nodeClick,
  });

  useEffect(() => {
    if (isLoading) return;
    setLoading(true);
    Promise.all([getConfiglist(nodeId || ''), getCollectorList()])
      .then()
      .catch((e) => {
        console.log(e)
      })
      .finally(() => {
        setLoading(false);
      })
    return () => {
      sessionStorage.removeItem('cloudRegionInfo');
    };
  }, [isLoading])

  useEffect(() => {
    if (!collectorId.length && !configdata.length) return;
    if (!loading) setLoading(true);
    Promise.resolve().then(() => {
      setTableData(configdata.filter((item) => {
        return collectorId.includes(item.collector);
      }));
      setLoading(false);
    });
  }, [collectorId, configdata])

  //获取配置文件列表
  const getConfiglist = async (search: string) => {
    const res = await Promise.all([getconfiglist(Number(cloudid), search), getnodelist({ cloud_region_id: Number(cloudid) })]);
    const configlist = res[0];
    const nodeList = res[1];
    const data = configlist.map((item: IConfiglistprops) => {
      const nodes = item.nodes?.map((node: string) => {
        const nodeItem = nodeList.find((nodeData: any) => nodeData.id === node);
        return {
          label: nodeItem?.ip,
          value: nodeItem?.id,
        };
      });
      const config = {
        key: item.id,
        name: item.name,
        collector: item.collector as string,
        collector_name: item.collector_name,
        operatingsystem: item.operating_system,
        nodecount: item.node_count,
        configinfo: item.config_template,
        nodes: nodes,
      };
      return config;
    });
    setConfigdata(data);
  };

  // 获取采集器列表
  const getCollectorList = async () => {
    const res = await getCollectorlist({});
    const filters = new Map();
    const collectorId =
      res
        .filter((item: any) => !item.controller_default_run)
        .map((item: any) => {
          filters.set(item.name, { text: item.name, value: item.name });
          return item.id;
        });
    setFilters(Array.from(filters.values()) as ColumnFilterItem[]);
    setCollectorId(collectorId);
  };

  //搜索框的触发事件
  const onSearch: SearchProps['onSearch'] = (value) => {
    setLoading(true);
    getConfiglist(value)
      .then()
      .catch((e) => {
        console.log(e);
      })
      .finally(() => {
        setLoading(false);
      })
  };

  // 子配置返回配置页面事件
  const handleCBack = () => {
    getConfiglist('');
    setShowSub(false);
  };

  // 弹窗确认成功后的回调
  const onSuccess = () => {
    if (!showSub) {
      setLoading(true);
      getConfiglist('')
        .then()
        .catch((e) => {
          console.log(e);
        }).finally(() => {
          setLoading(false);
        })
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
            cancel={() => handleCBack()}
            edit={hanldeSubEditClick}
            nodeData={nodeData}
          />
        )}
        {/* 弹窗组件（添加，编辑，应用）用于刷新页面 */}
        <ConfigModal
          ref={configurationRef}

          onSuccess={onSuccess}
        ></ConfigModal>
      </div>
    </Mainlayout>
  );
};

export default Configration;
