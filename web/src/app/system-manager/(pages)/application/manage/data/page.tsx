"use client";
import React, { useState, useEffect } from 'react';
import { Button, Input, Form, message, Spin, Popconfirm } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useTranslation } from '@/utils/i18n';
import CustomTable from '@/components/custom-table';
import OperateModal from '@/components/operate-modal';
import DynamicForm from '@/components/dynamic-form';
import PermissionRule from '@/app/system-manager/components/application/permissionRule';

const { Search } = Input;

interface DataItem {
  id: string;
  name: string;
  description: string;
  groupId: string;
  permissionRule?: {
    workspace: { type: string; allPermissions: { view: boolean; operate: boolean }; specificData: any[] };
    agent: { type: string; allPermissions: { view: boolean; operate: boolean }; specificData: any[] };
    tool: { type: string; allPermissions: { view: boolean; operate: boolean }; specificData: any[] };
  };
}

interface Group {
  id: string;
  name: string;
}

const DataManagement: React.FC = () => {
  const { t } = useTranslation();

  const [dataForm] = Form.useForm();
  const [dataList, setDataList] = useState<DataItem[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [dataModalOpen, setDataModalOpen] = useState(false);
  const [selectedData, setSelectedData] = useState<DataItem | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  // 模拟数据
  useEffect(() => {
    fetchGroups();
    fetchDataList();
  }, []);

  const fetchGroups = async () => {
    // 模拟从API获取分组数据
    setGroups([
      { id: '1', name: 'group1' },
      { id: '2', name: 'group2' },
      { id: '3', name: 'group3' },
    ]);
  };

  const fetchDataList = async (search?: string) => {
    setLoading(true);
    try {
      // 模拟API请求
      setTimeout(() => {
        const mockData: DataItem[] = [
          { id: '1', name: 'Data 1', description: 'Description for Data 1', groupId: '1' },
          { id: '2', name: 'Data 2', description: 'Description for Data 2', groupId: '2' },
          { id: '3', name: 'Data 3', description: 'Description for Data 3', groupId: '3' },
          { id: '4', name: 'Data 4', description: 'Description for Data 4', groupId: '1' },
        ];

        const filteredData = search
          ? mockData.filter(item =>
            item.name.toLowerCase().includes(search.toLowerCase()) ||
            item.description.toLowerCase().includes(search.toLowerCase())
          )
          : mockData;

        setDataList(filteredData);
        setTotal(filteredData.length);
        handleTableChange(1, pageSize);
        setLoading(false);
      }, 500);
    } catch (error) {
      console.error(`${t('common.fetchFailed')}:`, error);
      setLoading(false);
    }
  };

  const handleTableChange = (page: number, size?: number) => {
    const newPageSize = size || pageSize;

    setCurrentPage(page);
    setPageSize(newPageSize);
  };

  const showDataModal = (data: DataItem | null = null) => {
    setIsEditing(!!data);
    setSelectedData(data);

    // 定义默认的权限规则
    const defaultPermissionRule = {
      workspace: { type: 'all', allPermissions: { view: true, operate: true }, specificData: [] },
      agent: { type: 'all', allPermissions: { view: true, operate: true }, specificData: [] },
      tool: { type: 'all', allPermissions: { view: true, operate: true }, specificData: [] },
    };

    if (data) {
      dataForm.setFieldsValue({
        name: data.name,
        description: data.description,
        groupId: data.groupId,
        // 确保存在的权限规则被合并，而不是直接赋值
        permissionRule: data.permissionRule || defaultPermissionRule,
      });
    } else {
      dataForm.resetFields();
      // 明确设置默认权限规则
      dataForm.setFieldsValue({
        permissionRule: defaultPermissionRule,
      });
    }

    setDataModalOpen(true);
  };

  const handleDataModalSubmit = async () => {
    try {
      setModalLoading(true);
      await dataForm.validateFields();
      const values = dataForm.getFieldsValue();

      if (isEditing && selectedData) {
        // 模拟更新数据
        const updatedList = dataList.map(item =>
          item.id === selectedData.id ? { ...item, ...values } : item
        );
        setDataList(updatedList);
        message.success(t('common.updateSuccess'));
      } else {
        // 模拟添加数据
        const newItem: DataItem = {
          id: `${Date.now()}`,
          name: values.name,
          description: values.description,
          groupId: values.groupId,
        };
        setDataList([...dataList, newItem]);
        message.success(t('common.addSuccess'));
      }

      setDataModalOpen(false);
    } catch (error) {
      console.error('Failed:', error);
    } finally {
      setModalLoading(false);
    }
  };

  const handleDelete = (data: DataItem) => {
    // 模拟删除数据
    const updatedList = dataList.filter(item => item.id !== data.id);
    setDataList(updatedList);
    message.success(t('common.delSuccess'));
  };

  const handleSearch = (value: string) => {
    fetchDataList(value);
  };

  const columns = [
    {
      title: t('system.data.name'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('system.data.description'),
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: t('system.data.group'),
      dataIndex: 'groupId',
      key: 'groupId',
      render: (groupId: string) => {
        const group = groups.find(g => g.id === groupId);
        return group ? group.name : '-';
      }
    },
    {
      title: t('common.actions'),
      key: 'actions',
      render: (_: any, record: DataItem) => (
        <div className="flex space-x-2">
          <Button
            type="link"
            onClick={() => showDataModal(record)}
          >
            {t('common.edit')}
          </Button>
          <Popconfirm
            title={t('common.delConfirm')}
            okText={t('common.confirm')}
            cancelText={t('common.cancel')}
            onConfirm={() => handleDelete(record)}
          >
            <Button type="link">
              {t('common.delete')}
            </Button>
          </Popconfirm>
        </div>
      ),
    },
  ];

  const getFormFields = () => {
    return [
      {
        name: 'name',
        type: 'input',
        label: t('system.data.name'),
        placeholder: `${t('common.inputMsg')}${t('system.data.name')}`,
        rules: [{ required: true, message: `${t('common.inputMsg')}${t('system.data.name')}` }],
      },
      {
        name: 'description',
        type: 'textarea',
        label: t('system.data.description'),
        placeholder: `${t('common.inputMsg')}${t('system.data.description')}`,
        rows: 4,
      },
      {
        name: 'groupId',
        type: 'select',
        label: t('system.data.group'),
        placeholder: `${t('common.inputMsg')}${t('system.data.group')}`,
        rules: [{ required: true, message: `${t('common.inputMsg')}${t('system.data.group')}` }],
        options: groups.map(group => ({ value: group.id, label: group.name })),
      },
      {
        name: 'permissionRule',
        type: 'custom',
        label: t('system.permission.dataPermissionRule'),
        component: <PermissionRule />,
      },
    ];
  };

  return (
    <div className="w-full bg-[var(--color-bg)] rounded-md h-full p-4">
      <div className="flex justify-end mb-4">
        <Search
          allowClear
          enterButton
          className='w-60 mr-[8px]'
          onSearch={handleSearch}
          placeholder={`${t('common.search')}`}
        />
        <Button
          type="primary"
          onClick={() => showDataModal()}
          icon={<PlusOutlined />}
        >
          {t('common.add')}
        </Button>
      </div>

      <Spin spinning={loading}>
        <CustomTable
          scroll={{ y: 'calc(100vh - 245px)' }}
          columns={columns}
          dataSource={dataList}
          rowKey={(record) => record.id}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            onChange: handleTableChange,
          }}
        />
      </Spin>

      <OperateModal
        title={isEditing ? t('common.edit') : t('common.add')}
        okText={t('common.confirm')}
        cancelText={t('common.cancel')}
        okButtonProps={{ loading: modalLoading }}
        cancelButtonProps={{ disabled: modalLoading }}
        open={dataModalOpen}
        onOk={handleDataModalSubmit}
        onCancel={() => setDataModalOpen(false)}
      >
        <DynamicForm
          form={dataForm}
          fields={getFormFields()}
        />
      </OperateModal>
    </div>
  );
};

export default DataManagement;
