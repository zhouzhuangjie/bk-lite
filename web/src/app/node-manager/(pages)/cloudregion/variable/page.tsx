'use client';
import React, { useEffect, useRef, useState } from 'react';
import { Button, Input, message } from 'antd';
import CustomTable from '@/components/custom-table/index';
import { useTranslation } from '@/utils/i18n';
import VariableModal from './variableModal';
import { ModalRef } from '@/app/node-manager/types/index';
import { useVarColumns } from '@/app/node-manager/hooks/variable';
import type { GetProps } from 'antd';
import type { TableDataItem } from '@/app/node-manager/types/index';
import Mainlayout from '../mainlayout/layout';
import { PlusOutlined } from '@ant-design/icons';
import useApiCloudRegion from '@/app/node-manager/api/cloudregion';
import useApiClient from '@/utils/request';
import useCloudId from '@/app/node-manager/hooks/useCloudid';
import variableStyle from './index.module.scss';
type SearchProps = GetProps<typeof Input.Search>;
const { Search } = Input;

const Variable = () => {
  const { getvariablelist, deletevariable } = useApiCloudRegion();
  const { isLoading } = useApiClient();
  const variableRef = useRef<ModalRef>(null);
  const { t } = useTranslation();
  const cloudid = useCloudId();
  const [data, setData] = useState<TableDataItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!isLoading) {
      getVariablelist();
    }
  }, [isLoading]);

  //根据传入的值打开对应的用户弹窗（添加用户弹窗和编辑用户的弹窗）
  const openUerModal = (type: string, form: TableDataItem) => {
    variableRef.current?.showModal({
      type,
      form,
    });
  };
  //遍历数据，取出要回显的数据
  const getFormDataById = (key: string) => {
    const formData = data.find((item) => item.key === key);
    if (!formData) {
      throw new Error(`Form data not found for key: ${key}`);
    }
    return formData;
  };
  //删除的确定的弹窗
  const delconfirm = (key: string) => {
    deletevariable(key)
      .then(() => {
        message.success(t('common.delSuccess'));
      })
      .finally(() => {
        getVariablelist();
      });
  };

  const columns = useVarColumns({
    openUerModal,
    getFormDataById,
    delconfirm,
  });

  //添加和编辑成功后，重新获取表格数据
  const onsuccessvariablemodal = () => {
    getVariablelist();
  };

  //搜索框的事件
  const onSearch: SearchProps['onSearch'] = (value) => {
    getvariablelist(Number(cloudid), value).then((res) => {
      const tempdata = res.map((item: any) => {
        return {
          key: item.id,
          name: item.key,
          value: item.value,
          description: item.description,
        };
      });
      setData(tempdata);
    });
  };

  //获取表格数据
  const getVariablelist = () => {
    getvariablelist(Number(cloudid))
      .then((res) => {
        setLoading(true);
        const tempdata = res.map((item: any) => {
          return {
            key: item.id,
            name: item.key,
            value: item.value,
            description: item.description,
          };
        });
        setData(tempdata);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <Mainlayout>
      <div className={`${variableStyle.variable} w-full h-full`}>
        <div className="flex justify-end mb-4">
          <Search
            className="w-64 mr-[8px]"
            placeholder={t('common.search')}
            enterButton
            onSearch={onSearch}
          />
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
        </div>
        <div className="tablewidth">
          <CustomTable
            scroll={{ y: 'calc(100vh - 400px)', x: 'calc(100vw - 300px)' }}
            loading={loading}
            columns={columns}
            dataSource={data}
          />
        </div>
        <VariableModal
          ref={variableRef}
          onSuccess={onsuccessvariablemodal}
        ></VariableModal>
      </div>
    </Mainlayout>
  );
};
export default Variable;
