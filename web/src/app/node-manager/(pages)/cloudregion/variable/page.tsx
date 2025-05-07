'use client';
import React, { useEffect, useRef, useState } from 'react';
import { Button, Input, message } from 'antd';
import CustomTable from '@/components/custom-table';
import { useTranslation } from '@/utils/i18n';
import VariableModal from './variableModal';
import { ModalRef, TableDataItem } from '@/app/node-manager/types';
import { useVarColumns } from '@/app/node-manager/hooks/variable';
import type { GetProps } from 'antd';
import MainLayout from '../mainlayout/layout';
import { PlusOutlined } from '@ant-design/icons';
import useApiCloudRegion from '@/app/node-manager/api/cloudRegion';
import useApiClient from '@/utils/request';
import useCloudId from '@/app/node-manager/hooks/useCloudRegionId';
import variableStyle from './index.module.scss';
import PermissionWrapper from '@/components/permission';
type SearchProps = GetProps<typeof Input.Search>;
const { Search } = Input;

const Variable = () => {
  const cloudId = useCloudId();
  const { t } = useTranslation();
  const { isLoading } = useApiClient();
  const { getVariableList, deleteVariable } = useApiCloudRegion();
  const variableRef = useRef<ModalRef>(null);
  const [data, setData] = useState<TableDataItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchText, setSearchText] = useState<string>('');

  useEffect(() => {
    if (!isLoading) {
      getTablelist();
    }
  }, [isLoading]);

  const openUerModal = (type: string, form: TableDataItem) => {
    variableRef.current?.showModal({
      type,
      form,
    });
  };

  //遍历数据，取出要回显的数据
  const getFormDataById = (key: string) => {
    return data.find((item) => item.key === key) || {};
  };

  const delConfirm = (key: string) => {
    setLoading(true);
    deleteVariable(key)
      .then(() => {
        message.success(t('common.delSuccess'));
        getTablelist();
      })
      .catch(() => {
        setLoading(false);
      });
  };

  const columns = useVarColumns({
    openUerModal,
    getFormDataById,
    delConfirm,
  });

  const onSearch: SearchProps['onSearch'] = (value) => {
    setSearchText(value);
    getTablelist(value);
  };

  //获取表格数据
  const getTablelist = async (search = searchText) => {
    setLoading(true);
    try {
      const res = await getVariableList({
        cloud_region_id: cloudId,
        search,
      });
      const tempdata = res.map((item: any) => {
        return {
          ...item,
          key: item.id,
          name: item.key,
        };
      });
      setData(tempdata);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className={`${variableStyle.variable} w-full h-full`}>
        <div className="flex justify-end mb-4">
          <Search
            className="w-64 mr-[8px]"
            placeholder={t('common.search')}
            enterButton
            onSearch={onSearch}
          />
          <PermissionWrapper requiredPermissions={['Add']}>
            <Button
              type="primary"
              onClick={() => {
                openUerModal('add', {
                  name: '',
                  key: '',
                  value: '',
                  description: '',
                });
              }}
            >
              <PlusOutlined />
              {t('common.add')}
            </Button>
          </PermissionWrapper>
        </div>
        <div className="tablewidth">
          <CustomTable
            scroll={{ y: 'calc(100vh - 326px)', x: 'calc(100vw - 300px)' }}
            loading={loading}
            columns={columns}
            dataSource={data}
          />
        </div>
        <VariableModal
          ref={variableRef}
          onSuccess={() => getTablelist()}
        ></VariableModal>
      </div>
    </MainLayout>
  );
};
export default Variable;
