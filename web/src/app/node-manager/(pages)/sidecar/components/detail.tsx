'use client';
import React, { useEffect, useState } from 'react';
import { useTranslation } from '@/utils/i18n';
import { message } from 'antd';
import CustomTable from '@/components/custom-table';
import { useDetailColumns } from '@/app/node-manager/hooks/collector';
import useApiCollector from '@/app/node-manager/api/collector';
import type {  Pagination, TableDataItem } from '@/app/node-manager/types/index';

const Collectordetail = () => {
  const { t } = useTranslation();
  const { getPackageList, deletePackage } = useApiCollector();
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
  }, [])


  const getTableData = async () => {
    const searchParams = new URLSearchParams(window.location.search);
    const info = {
      name: searchParams.get('name') || '',
      system: [searchParams.get('system') || ''],
    };
    try {
      setTableLoading(true);
      const getPackage = getPackageList({ object: info.name, os: info.system[0] });
      const res = await Promise.all([getPackage]);
      const packageInfo = res[0];
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
  };

  const handleTableChange = (pagination: any) => {
    setPagination((prev: Pagination) => ({
      total: prev.total,
      ...pagination
    }));
  };

  return (
    <div className="w-full h-full">
      <CustomTable
        scroll={{ y: 'calc(100vh - 440px)', x: 'calc(100vw - 320px)' }}
        columns={columns}
        dataSource={tableData}
        pagination={pagination}
        loading={tableLoading}
        rowKey="id"
        onChange={handleTableChange}
      />
    </div>
  );
};

export default Collectordetail;
