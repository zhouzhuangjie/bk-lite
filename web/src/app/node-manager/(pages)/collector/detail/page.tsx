'use client';
import React, { useEffect, useState } from 'react';
import { Button, message, Popconfirm } from 'antd';
import { ColumnItem } from '@/types';
import Icon from '@/components/icon';
import { useTranslation } from '@/utils/i18n';
import { useRouter } from 'next/navigation';
import CustomTable from '@/components/custom-table';
// import Permission from '@/components/permission';
import SubLayout from '@/components/sub-layout';
import { useLocalizedTime } from '@/hooks/useLocalizedTime';
import useApiCollector from '@/app/node-manager/api/collector';
import type { Collectorcardprops, Pagination, TableDataItem } from '@/app/node-manager/types/index';

const Collectordetail = () => {
  const router = useRouter();
  const { t } = useTranslation();
  const { convertToLocalizedTime } = useLocalizedTime();
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
  const columns: ColumnItem[] = [
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
      id: searchParams.get('id') || '' ,
      name: searchParams.get('name') || '',
      system: [searchParams.get('system') || ''],
      introduction: searchParams.get('introduction') || '',
    }
    try {
      setTableLoading(true);
      const getPackage = getPackageList({ object: info.name, os: info.system[0] });
      const res = await Promise.all([getPackage]);
      const packageInfo = res[0];
      setDetaildata(info);
      setTableData(packageInfo || []);
      setTableLoading(false);
    } catch (error) {
      console.log(error);
    }
    setPagination((prev: Pagination) => ({
      ...prev,
      current: 1,
    }));
    setTableLoading(false);
  };

  const handleDelete = (id: number) => {
    setTableLoading(true);
    deletePackage(id).then(() => {
      getTableData();
      message.success(t('common.delSuccess'));
      setTableLoading(false);
    }).catch(() => {
      setTableLoading(false)
    })
  }

  const handleTableChange = () => {
    setPagination((prev: Pagination) => ({
      ...prev,
      current: 1,
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
