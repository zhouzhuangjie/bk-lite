'use client';
import React, {
  useState,
  useRef,
  forwardRef,
  useImperativeHandle,
  useEffect,
  useCallback,
} from 'react';
import { Form, Select, message, Button, Input, Popconfirm } from 'antd';
import { EditOutlined } from '@ant-design/icons';
import OperateModal from '@/components/operate-modal';
import type { FormInstance } from 'antd';
import { useTranslation } from '@/utils/i18n';
import { ModalSuccess, ModalRef } from '@/app/node-manager/types/index';
import useApiCloudRegion from '@/app/node-manager/api/cloudregion';
import type { TableDataItem } from '@/app/node-manager/types/index';
import useCloudId from '@/app/node-manager/hooks/useCloudid';
import { OPERATE_SYSTEMS } from '@/app/node-manager/constants/cloudregion';
import { ControllerInstallFields } from '@/app/node-manager/types/cloudregion';
import CustomTable from '@/components/custom-table';
import BatchEditModal from './batchEditModal';
import { cloneDeep } from 'lodash';
const { Option } = Select;

const ControllerUninstall = forwardRef<ModalRef, ModalSuccess>(
  ({ onSuccess, config }, ref) => {
    const collectorformRef = useRef<FormInstance>(null);
    const { t } = useTranslation();
    const cloudid = useCloudId();
    const { getnodelist, uninstallController } = useApiCloudRegion();
    const tableFormRef = useRef<FormInstance>(null);
    const instRef = useRef<ModalRef>(null);
    const currentTableData = useRef<TableDataItem[]>([]);
    const [type, setType] = useState<string>('uninstallSidecar');
    const [collectorVisible, setCollectorVisible] = useState<boolean>(false);
    //需要二次弹窗确定的类型
    const Popconfirmarr = ['uninstallSidecar'];
    const [collectorLoading, setCollectorLoading] = useState<boolean>(false);
    const [confirmLoading, setConfirmLoading] = useState<boolean>(false);
    const [nodeList, setNodeList] = useState<TableDataItem[]>([]);
    const [tableData, setTableData] = useState<TableDataItem[]>([]);
    const tableColumns: any = [
      {
        title: t('node-manager.cloudregion.node.ipAdrress'),
        dataIndex: 'ip',
        width: 100,
        key: 'ip',
      },
      {
        title: (
          <>
            {t('node-manager.cloudregion.node.loginPort')}
            <EditOutlined
              className="cursor-pointer ml-[10px] text-[var(--color-primary)]"
              onClick={() => batchEditModal('port')}
            />
          </>
        ),
        dataIndex: 'port',
        width: 100,
        key: 'port',
        render: (value: string, row: TableDataItem) => {
          return (
            <>
              <Form.Item name={`port-${row.id}`}>
                <Input onBlur={(e) => handleInputBlur(e, row, 'port')}></Input>
              </Form.Item>
            </>
          );
        },
      },
      {
        title: (
          <>
            {t('node-manager.cloudregion.node.loginAccount')}
            <EditOutlined
              className="cursor-pointer ml-[10px] text-[var(--color-primary)]"
              onClick={() => batchEditModal('username')}
            />
          </>
        ),
        dataIndex: 'username',
        width: 100,
        key: 'username',
        render: (value: string, row: TableDataItem) => {
          return (
            <>
              <Form.Item name={`username-${row.id}`}>
                <Input
                  onBlur={(e) => handleInputBlur(e, row, 'username')}
                ></Input>
              </Form.Item>
            </>
          );
        },
      },
      {
        title: (
          <>
            {t('node-manager.cloudregion.node.loginPassword')}
            <EditOutlined
              className="cursor-pointer ml-[10px] text-[var(--color-primary)]"
              onClick={() => batchEditModal('password')}
            />
          </>
        ),
        dataIndex: 'password',
        width: 100,
        key: 'password',
        render: (value: string, row: TableDataItem) => {
          return (
            <>
              <Form.Item name={`password-${row.id}`}>
                <Input.Password
                  onBlur={(e) => handleInputBlur(e, row, 'password')}
                ></Input.Password>
              </Form.Item>
            </>
          );
        },
      },
    ];

    const handleBatchEdit = useCallback(
      (row: TableDataItem) => {
        const data = cloneDeep(currentTableData.current);
        const obj: any = {};
        data.forEach((item) => {
          item[row.field] = row.value;
          obj[`${row.field}-${item.id}`] = row.value;
        });
        tableFormRef.current?.setFieldsValue(obj);
        currentTableData.current = data;
        setTableData(data);
      },
      [currentTableData]
    );

    useImperativeHandle(ref, () => ({
      showModal: ({ type, form }) => {
        setCollectorVisible(true);
        setType(type);
        const list = (form?.list || []).map((item: TableDataItem) => ({
          id: item.id,
          os: item.operating_system,
          ip: item.ip,
          port: null,
          username: null,
          password: null,
        }));
        currentTableData.current = list;
        setTableData(list);
        initPage();
      },
    }));

    useEffect(() => {
      if (tableData?.length && tableFormRef.current) {
        const obj = tableFormRef.current.getFieldsValue() || {};
        setTimeout(() => {
          tableFormRef.current?.setFieldsValue(cloneDeep(obj));
        });
      }
    }, [tableData]);

    useEffect(() => {
      collectorformRef.current?.resetFields();
    }, [collectorformRef]);

    const batchEditModal = (field: string) => {
      instRef.current?.showModal({
        title: t('common.bulkEdit'),
        type: field,
        form: {},
      });
    };

    const handleInputBlur = (
      e: React.ChangeEvent<HTMLInputElement>,
      row: TableDataItem,
      key: string
    ) => {
      const data = cloneDeep(currentTableData.current);
      const index = data.findIndex((item) => item.id === row.id);
      if (index !== -1) {
        data[index][key] = e.target.value;
        currentTableData.current = data;
      }
    };

    const initPage = async () => {
      setCollectorLoading(true);
      try {
        const res = await getnodelist({
          cloud_region_id: Number(cloudid),
          operating_system: config.os,
        });
        setNodeList(res || []);
      } finally {
        setCollectorLoading(false);
      }
    };

    //关闭用户的弹窗(取消和确定事件)
    const handleCancel = () => {
      setCollectorVisible(false);
      setCollectorLoading(false);
    };

    const validateTableData = async () => {
      const data = cloneDeep(currentTableData.current);
      if (!data.length) {
        return Promise.reject(new Error(t('common.required')));
      }
      if (
        data.every((item) => Object.values(item).every((tex) => !!tex?.length))
      ) {
        return Promise.resolve();
      }
      return Promise.reject(new Error(t('common.valueValidate')));
    };

    //点击确定按钮的相关逻辑处理
    const handleConfirm = () => {
      collectorformRef.current?.validateFields().then((values) => {
        const data = cloneDeep(currentTableData.current);
        const params = {
          cloud_region_id: +cloudid,
          work_node: values.work_node,
          nodes: data.map((item) => {
            delete item.id;
            return {
              ...item,
              port: +item.port,
            };
          }),
        };
        uninstall(params);
      });
    };

    const uninstall = async (params = {}) => {
      setConfirmLoading(true);
      try {
        const data = await uninstallController(params);
        message.success(t('common.operationSuccessful'));
        handleCancel();
        onSuccess({
          taskId: data.task_id,
          type: 'uninstallController',
        });
      } finally {
        setConfirmLoading(false);
      }
    };

    return (
      <OperateModal
        title={t(`node-manager.cloudregion.node.${type}`)}
        open={collectorVisible}
        width={600}
        destroyOnClose
        okText={t('common.confirm')}
        cancelText={t('common.cancel')}
        onCancel={handleCancel}
        footer={
          <>
            <Button key="back" onClick={handleCancel}>
              {t('common.cancel')}
            </Button>
            {Popconfirmarr.includes(type) ? (
              <Popconfirm
                title={t(`node-manager.cloudregion.node.${type}`)}
                description={t(`node-manager.cloudregion.node.${type}Info`)}
                okText={t('common.confirm')}
                cancelText={t('common.cancel')}
                onConfirm={handleConfirm}
              >
                <Button type="primary" loading={confirmLoading}>
                  {t('common.confirm')}
                </Button>
              </Popconfirm>
            ) : (
              <Button
                type="primary"
                loading={confirmLoading}
                onClick={handleConfirm}
              >
                {t('common.confirm')}
              </Button>
            )}
          </>
        }
      >
        <Form ref={collectorformRef} layout="vertical" colon={false}>
          <Form.Item<ControllerInstallFields>
            required
            label={t('node-manager.cloudregion.node.defaultNode')}
          >
            <Form.Item
              name="work_node"
              noStyle
              rules={[{ required: true, message: t('common.required') }]}
            >
              <Select
                style={{
                  width: 300,
                }}
                showSearch
                allowClear
                loading={collectorLoading}
                placeholder={t('common.pleaseSelect')}
              >
                {nodeList.map((item) => (
                  <Option value={item.id} key={item.id}>
                    {item.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <div className="text-[var(--color-text-2)] text-[12px] mt-[10px]">
              {t('node-manager.cloudregion.node.defaultUninstallNodeDes')}
            </div>
          </Form.Item>
          <Form.Item<ControllerInstallFields>
            name="nodes"
            label={t('node-manager.cloudregion.node.controllerInfo')}
            rules={[{ required: true, validator: validateTableData }]}
          >
            <Form ref={tableFormRef} component={false}>
              <CustomTable
                rowKey="id"
                columns={tableColumns}
                dataSource={tableData}
              />
            </Form>
          </Form.Item>
        </Form>
        <BatchEditModal
          ref={instRef}
          config={{
            systemList: OPERATE_SYSTEMS,
            groupList: [],
          }}
          onSuccess={handleBatchEdit}
        />
      </OperateModal>
    );
  }
);
ControllerUninstall.displayName = 'controllerUninstall';
export default ControllerUninstall;
