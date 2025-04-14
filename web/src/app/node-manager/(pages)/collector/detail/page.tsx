'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslation } from '@/utils/i18n';
import { message } from 'antd';
import Icon from '@/components/icon';
import CustomTable from '@/components/custom-table';
import SubLayout from '@/components/sub-layout';
import { useDetailColumns } from '@/app/node-manager/hooks/collector';
import useApiCollector from '@/app/node-manager/api/collector';
import type { Collectorcardprops, Pagination, TableDataItem } from '@/app/node-manager/types/index';

const Collectordetail = () => {
  const router = useRouter();
  const { t } = useTranslation();
  const { getPackageList, deletePackage } = useApiCollector();
  const [detaildata, setDetaildata] = useState<Collectorcardprops>({
    id: '',
    name: '',
    system: [],
    introduction: '',
  });
  const [pagination, setPagination] = useState<Pagination>({
    current: 1,
    total: 0,
    pageSize: 20,
  });
  const [tableData, setTableData] = useState<TableDataItem[]>([]);
  const [tableLoading, setTableLoading] = useState<boolean>(false);
  const columns = useDetailColumns({
    handleDelete: (id) => handleDelete(id),
  });

  useEffect(() => {
    getTableData();
  }, []);

  //顶部的组件
  const Topsection = () => {
    return (
      <div className="flex flex-col h-[90px] p-4 overflow-hidden">
        <h1 className="text-lg">{t('node-manager.collector.title')}</h1>
        <p className="text-sm overflow-hidden w-full min-w-[1000px] mt-[8px]">
          {detaildata.introduction}
        </p>
      </div>
    );
  };

  const Collectorintro = () => {
    return (
      <div className="h-[58px] flex flex-col justify-items-center">
        <div className="flex justify-center mb-[8px]">
          <Icon
            type="caijiqizongshu"
            style={{ height: '34px', width: '34px' }}
          ></Icon>
        </div>
        <div className="flex justify-center">
          <div>{detaildata.name}</div>
        </div>
      </div>
    );
  };

  const getTableData = async () => {
    const searchParams = new URLSearchParams(window.location.search);
    const info = {
      id: searchParams.get('id') || '',
      name: searchParams.get('name') || '',
      system: [searchParams.get('system') || ''],
      introduction: searchParams.get('introduction') || '',
    };
    try {
      setTableLoading(true);
      const getPackage = getPackageList({ object: info.name, os: info.system[0] });
      const res = await Promise.all([getPackage]);
      const packageInfo = res[0];
      setDetaildata(info);
      setTableData(packageInfo || []);
      setPagination((prev: Pagination) => ({
        ...prev,
        total: packageInfo.length,
        current: 1,
      }));
    } catch (error) {
      console.log(error);
    }
    setTableLoading(false);
  };

  const handleDelete = (id: number) => {
    setTableLoading(true);
    deletePackage(id).then(() => {
      getTableData();
      message.success(t('common.delSuccess'));
    }).catch((e) => {
      console.log(e);
    }).finally(() => {
      setTableLoading(false);
    })
  }

  const handleTableChange = (pagination: any) => {
    console.log(pagination);
    setPagination((prev: Pagination) => ({
      total: prev.total,
      ...pagination
    }));
  }

  return (
    <div className="w-full h-full">
      <SubLayout
        topSection={<Topsection></Topsection>}
        showBackButton={true}
        intro={<Collectorintro></Collectorintro>}
        onBackButtonClick={() => {
          router.push('/node-manager/collector/');
        }}
      >
        <CustomTable
          scroll={{ y: 'calc(100vh - 440px)', x: 'calc(100vw - 320px)' }}
          columns={columns}
          dataSource={tableData}
          pagination={pagination}
          loading={tableLoading}
          rowKey="id"
          onChange={handleTableChange}
        />
      </SubLayout>
    </div>
  );
};

export default Collectordetail;
