'use client';
import React, {
  useState,
  useRef,
  forwardRef,
  useImperativeHandle,
  useEffect,
} from 'react';
import { Form, Select, message, Button, Popconfirm } from 'antd';
import OperateModal from '@/components/operate-modal';
import type { FormInstance } from 'antd';
import { useTranslation } from '@/utils/i18n';
import { ModalSuccess, ModalRef } from '@/app/node-manager/types/index';
import useApiCollector from '@/app/node-manager/api/collector';
import useApiCloudRegion from '@/app/node-manager/api/cloudregion';
import type { TableDataItem } from '@/app/node-manager/types/index';
const { Option } = Select;

const CollectorModal = forwardRef<ModalRef, ModalSuccess>(
  ({ onSuccess }, ref) => {
    const collectorformRef = useRef<FormInstance>(null);
    const { t } = useTranslation();
    const { getCollectorlist, getPackageList } = useApiCollector();
    const { installCollector, batchoperationcollector } = useApiCloudRegion();
    const [type, setType] = useState<string>('installCollector');
    const [nodeIds, setNodeIds] = useState<string[]>(['']);
    const [collectorVisible, setCollectorVisible] = useState<boolean>(false);
    //需要二次弹窗确定的类型
    const Popconfirmarr = ['restartCollector', 'uninstallCollector'];
    const [packageList, setPackageList] = useState<TableDataItem[]>([]);
    const [collectorlist, setCollectorlist] = useState<TableDataItem[]>([]);
    const [versionLoading, setVersionLoading] = useState<boolean>(false);
    const [collectorLoading, setCollectorLoading] = useState<boolean>(false);
    const [confirmLoading, setConfirmLoading] = useState<boolean>(false);
    const [collector, setCollector] = useState<string | null>(null);
    const [system, setSystem] = useState<string>('');

    useImperativeHandle(ref, () => ({
      showModal: ({ type, ids, selectedsystem }) => {
        setCollectorVisible(true);
        setType(type);
        setSystem(selectedsystem as string);
        setNodeIds(ids || []);
        initPage(selectedsystem || '');
      },
    }));

    useEffect(() => {
      collectorformRef.current?.resetFields();
    }, [collectorformRef]);

    const initPage = async (selectedsystem: string) => {
      setCollectorLoading(true);
      try {
        const data = await getCollectorlist({
          node_operating_system: selectedsystem,
        });
        setCollectorlist(data);
      } finally {
        setCollectorLoading(false);
      }
    };

    //关闭用户的弹窗(取消和确定事件)
    const handleCancel = () => {
      setCollectorVisible(false);
      setVersionLoading(false);
      setCollectorLoading(false);
    };

    //点击确定按钮的相关逻辑处理
    const handleConfirm = () => {
      //表单验证
      collectorformRef.current?.validateFields().then((values) => {
        let request: any = installCollector;
        let params: any = {
          nodes: nodeIds,
          collector_package: values.version,
        };
        switch (type) {
          case 'startCollector':
            params = {
              node_ids: nodeIds,
              collector_id: collector,
              operation: 'start',
            };
            request = batchoperationcollector;
            break;
          case 'restartCollector':
            params = {
              node_ids: nodeIds,
              collector_id: collector,
              operation: 'restart',
            };
            request = batchoperationcollector;
            break;
          default:
            break;
        }
        operate(request, params);
      });
    };

    const operate = async (callback: any, params: any) => {
      try {
        setConfirmLoading(true);
        const data = await callback(params);
        const config = {
          taskId: data.task_id || '',
          type,
        };
        message.success(t('common.operationSuccessful'));
        handleCancel();
        onSuccess(config);
      } finally {
        setConfirmLoading(false);
      }
    };

    const handleCollectorChange = async (value: string) => {
      setCollector(value);
      setPackageList([]);
      collectorformRef.current?.setFieldsValue({
        version: null,
      });
      const object = collectorlist.find(
        (item: TableDataItem) => item.id === value
      )?.name;
      if (type === 'installCollector' && value) {
        try {
          setVersionLoading(true);
          const data = await getPackageList({ object, os: system });
          setPackageList(data);
        } finally {
          setVersionLoading(false);
        }
      }
    };

    return (
      <OperateModal
        title={t(`node-manager.cloudregion.node.${type}`)}
        open={collectorVisible}
        destroyOnClose
        okText={t('common.confirm')}
        cancelText={t('common.cancel')}
        onCancel={handleCancel}
        footer={
          <>
            <Button key="back" loading={confirmLoading} onClick={handleCancel}>
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
                <Button type="primary">{t('common.confirm')}</Button>
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
          <Form.Item
            name="Collector"
            label={t('node-manager.cloudregion.node.collector')}
            rules={[
              {
                required: true,
                message: t('common.required'),
              },
            ]}
          >
            <Select
              value={collector}
              loading={collectorLoading}
              showSearch
              allowClear
              onChange={handleCollectorChange}
            >
              {collectorlist.map((item) => (
                <Option value={item.id} key={item.id}>
                  {item.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          {type === 'installCollector' && (
            <Form.Item
              name="version"
              label={t('node-manager.cloudregion.node.version')}
              rules={[
                {
                  required: true,
                  message: t('common.required'),
                },
              ]}
            >
              <Select showSearch allowClear loading={versionLoading}>
                {packageList.map((item) => (
                  <Option value={item.id} key={item.id}>
                    {item.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>
          )}
        </Form>
      </OperateModal>
    );
  }
);
CollectorModal.displayName = 'CollectorModal';
export default CollectorModal;
