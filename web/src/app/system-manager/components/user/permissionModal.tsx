import React, { useEffect } from 'react';
import { Form, Input, Select } from 'antd';
import type { DataNode as TreeDataNode } from 'antd/lib/tree';
import { useTranslation } from '@/utils/i18n';
import OperateModal from '@/components/operate-modal';
import CustomTable from '@/components/custom-table';

interface PermissionModalProps {
  visible: boolean;
  node: TreeDataNode | null;
  onOk: (values: any) => void;
  onCancel: () => void;
}

export interface AppPermission {
  key: string;
  app: string;
  permission: 'rule' | 'full';
}

const PermissionModal: React.FC<PermissionModalProps> = ({ visible, node, onOk, onCancel }) => {
  const { t } = useTranslation();
  const [form] = Form.useForm();

  // 每次弹窗打开时重置表单值
  useEffect(() => {
    if (visible && node) {
      form.setFieldsValue({
        groupName: typeof node?.title === 'string' ? node.title : ''
      });
    }
  }, [visible, node, form]);

  const appData: AppPermission[] = [
    { key: '1', app: '应用1', permission: 'rule' },
    { key: '2', app: '应用2', permission: 'full' },
    { key: '3', app: '应用3', permission: 'full' },
  ]

  const columns = [
    {
      title: t('system.permission.app'),
      dataIndex: 'app',
      key: 'app',
    },
    {
      title: t('system.permission.dataPermission'),
      dataIndex: 'permission',
      key: 'permission',
      render: (text: string, record: AppPermission) => (
        <Select
          defaultValue={text}
          className="w-full"
          options={[
            { value: 'full', label: t('system.permission.fullPermission') },
            { value: 'rule', label: t('system.permission.dataPermissionRule') },
          ]}
          onChange={(value) => {
            const newData = [...appData];
            const index = newData.findIndex(item => item.key === record.key);
            if (index > -1) {
              newData[index].permission = value as 'full' | 'rule';
            }
          }}
        />
      ),
    },
  ];

  const handleOk = () => {
    form.validateFields().then(values => {
      onOk({ ...values, permissions: appData });
    });
  };

  return (
    <OperateModal
      title={t('system.permission.setDataPermission')}
      open={visible}
      onOk={handleOk}
      onCancel={() => {
        form.resetFields();
        onCancel();
      }}
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Form.Item
          name="groupName"
          label={t('system.permission.group')}
          rules={[{ required: true, message: t('system.permission.pleaseInputGroupName') }]}
        >
          <Input />
        </Form.Item>
        <Form.Item label={t('system.permission.dataPermission')}>
          <CustomTable
            columns={columns}
            dataSource={appData}
            pagination={false}
            size="small"
            rowKey="key"
            bordered={false}
          />
        </Form.Item>
      </Form>
    </OperateModal>
  );
};

export default PermissionModal;
