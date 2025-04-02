import React, { useState, useEffect } from 'react';
import { Tabs, Radio, Checkbox, Table, Form } from 'antd';
import type { RadioChangeEvent } from 'antd';
import type { CheckboxChangeEvent } from 'antd/es/checkbox';

interface PermissionRuleProps {
  value?: any;
  onChange?: (value: any) => void;
}

interface DataPermission {
  id: string;
  name: string;
  view: boolean;
  operate: boolean;
}

// 权限配置接口
interface PermissionConfig {
  type: string;
  allPermissions: {
    view: boolean;
    operate: boolean;
  };
  specificData: Array<DataPermission>;
}

// 带索引签名的权限状态接口
interface PermissionsState {
  [key: string]: PermissionConfig;
}

const PermissionRule: React.FC<PermissionRuleProps> = ({ value = {}, onChange }) => {
  // 创建默认权限配置
  const defaultPermissions: PermissionsState = {
    workspace: { type: 'all', allPermissions: { view: true, operate: true }, specificData: [] },
    agent: { type: 'all', allPermissions: { view: true, operate: true }, specificData: [] },
    tool: { type: 'all', allPermissions: { view: true, operate: true }, specificData: [] },
  };

  // 确保初始值合并默认值
  const [permissions, setPermissions] = useState<PermissionsState>(() => {
    return {
      workspace: {
        type: value?.workspace?.type || 'all',
        allPermissions: {
          view: value?.workspace?.allPermissions?.view ?? true,
          operate: value?.workspace?.allPermissions?.operate ?? true
        },
        specificData: value?.workspace?.specificData || []
      },
      agent: {
        type: value?.agent?.type || 'all',
        allPermissions: {
          view: value?.agent?.allPermissions?.view ?? true,
          operate: value?.agent?.allPermissions?.operate ?? true
        },
        specificData: value?.agent?.specificData || []
      },
      tool: {
        type: value?.tool?.type || 'all',
        allPermissions: {
          view: value?.tool?.allPermissions?.view ?? true,
          operate: value?.tool?.allPermissions?.operate ?? true
        },
        specificData: value?.tool?.specificData || []
      }
    };
  });

  // 监听外部传入的value变化
  useEffect(() => {
    if (value && Object.keys(value).length > 0) {
      // 合并默认值和传入的value，确保结构完整
      const newPermissions: PermissionsState = {
        workspace: {
          type: value?.workspace?.type || 'all',
          allPermissions: {
            view: value?.workspace?.allPermissions?.view ?? true,
            operate: value?.workspace?.allPermissions?.operate ?? true
          },
          specificData: value?.workspace?.specificData || []
        },
        agent: {
          type: value?.agent?.type || 'all',
          allPermissions: {
            view: value?.agent?.allPermissions?.view ?? true,
            operate: value?.agent?.allPermissions?.operate ?? true
          },
          specificData: value?.agent?.specificData || []
        },
        tool: {
          type: value?.tool?.type || 'all',
          allPermissions: {
            view: value?.tool?.allPermissions?.view ?? true,
            operate: value?.tool?.allPermissions?.operate ?? true
          },
          specificData: value?.tool?.specificData || []
        }
      };
      setPermissions(newPermissions);
    }
  }, [value]);

  const [activeKey, setActiveKey] = useState('workspace');

  // 模拟数据
  const mockData: { [key: string]: DataPermission[] } = {
    workspace: [
      { id: '1', name: '工作台数据1', view: true, operate: false },
      { id: '2', name: '工作台数据2', view: false, operate: false },
    ],
    agent: [
      { id: '1', name: '智能体数据1', view: true, operate: false },
      { id: '2', name: '智能体数据2', view: false, operate: false },
    ],
    tool: [
      { id: '1', name: '工具数据1', view: true, operate: false },
      { id: '2', name: '工具数据2', view: false, operate: false },
    ],
  };

  const handleTypeChange = (e: RadioChangeEvent, tab: string) => {
    const newPermissions = { ...permissions };
    if (newPermissions[tab]) {
      newPermissions[tab].type = e.target.value;
      setPermissions(newPermissions);
      if (onChange) {
        onChange(newPermissions);
      }
    }
  };

  const handleAllPermissionChange = (e: CheckboxChangeEvent, tab: string, type: 'view' | 'operate') => {
    const newPermissions = { ...permissions };
    if (newPermissions[tab] && newPermissions[tab].allPermissions) {
      newPermissions[tab].allPermissions[type] = e.target.checked;
      setPermissions(newPermissions);
      if (onChange) {
        onChange(newPermissions);
      }
    }
  };

  const handleSpecificDataChange = (record: DataPermission, tab: string, type: 'view' | 'operate') => {
    const newPermissions = { ...permissions };
    if (!newPermissions[tab]) {
      newPermissions[tab] = defaultPermissions[tab];
    }
    if (!newPermissions[tab].specificData) {
      newPermissions[tab].specificData = [];
    }

    const dataIndex = newPermissions[tab].specificData.findIndex(item => item.id === record.id);

    if (dataIndex === -1) {
      // 如果数据不存在，添加新数据
      newPermissions[tab].specificData.push({
        id: record.id,
        name: record.name,
        view: type === 'view' ? !record.view : record.view,
        operate: type === 'operate' ? !record.operate : record.operate
      });
    } else {
      // 更新现有数据
      newPermissions[tab].specificData[dataIndex][type] = !newPermissions[tab].specificData[dataIndex][type];
    }

    setPermissions(newPermissions);
    if (onChange) {
      onChange(newPermissions);
    }
  };

  const columns = [
    {
      title: '数据',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: DataPermission) => {
        // 查找记录是否在当前选择的特定数据中
        const specificData = permissions[activeKey].specificData;
        const currentData = specificData.find(item => item.id === record.id);
        const isViewChecked = currentData ? currentData.view : record.view;
        const isOperateChecked = currentData ? currentData.operate : record.operate;

        return (
          <div className="flex space-x-4">
            <Checkbox
              checked={isViewChecked}
              onChange={() => handleSpecificDataChange(record, activeKey, 'view')}
            >
              查看
            </Checkbox>
            <Checkbox
              checked={isOperateChecked}
              onChange={() => handleSpecificDataChange(record, activeKey, 'operate')}
            >
              操作
            </Checkbox>
          </div>
        );
      },
    },
  ];

  const items = [
    {
      key: 'workspace',
      label: '工作台',
      children: (
        <div className="p-4">
          <div className="mb-4">
            <Form.Item label="类型" className="mb-2">
              <Radio.Group
                value={permissions.workspace.type}
                onChange={(e) => handleTypeChange(e, 'workspace')}
              >
                <Radio value="all">全部数据</Radio>
                <Radio value="specific">指定数据</Radio>
              </Radio.Group>
            </Form.Item>

            {permissions.workspace.type === 'all' ? (
              <Form.Item label="权限" className="mt-4">
                <div className="flex space-x-4">
                  <Checkbox
                    checked={permissions.workspace.allPermissions.view}
                    onChange={(e) => handleAllPermissionChange(e, 'workspace', 'view')}
                  >
                    查看
                  </Checkbox>
                  <Checkbox
                    checked={permissions.workspace.allPermissions.operate}
                    onChange={(e) => handleAllPermissionChange(e, 'workspace', 'operate')}
                  >
                    操作
                  </Checkbox>
                </div>
              </Form.Item>
            ) : (
              <Table
                rowKey="id"
                columns={columns}
                dataSource={mockData.workspace}
                pagination={false}
                className="mt-4"
              />
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'agent',
      label: '智能体',
      children: (
        <div className="p-4">
          <div className="mb-4">
            <Form.Item label="类型" className="mb-2">
              <Radio.Group
                value={permissions.agent.type}
                onChange={(e) => handleTypeChange(e, 'agent')}
              >
                <Radio value="all">全部数据</Radio>
                <Radio value="specific">指定数据</Radio>
              </Radio.Group>
            </Form.Item>

            {permissions.agent.type === 'all' ? (
              <Form.Item label="权限" className="mt-4">
                <div className="flex space-x-4">
                  <Checkbox
                    checked={permissions.agent.allPermissions.view}
                    onChange={(e) => handleAllPermissionChange(e, 'agent', 'view')}
                  >
                    查看
                  </Checkbox>
                  <Checkbox
                    checked={permissions.agent.allPermissions.operate}
                    onChange={(e) => handleAllPermissionChange(e, 'agent', 'operate')}
                  >
                    操作
                  </Checkbox>
                </div>
              </Form.Item>
            ) : (
              <Table
                rowKey="id"
                columns={columns}
                dataSource={mockData.agent}
                pagination={false}
                className="mt-4"
              />
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'tool',
      label: '工具',
      children: (
        <div className="p-4">
          <div className="mb-4">
            <Form.Item label="类型" className="mb-2">
              <Radio.Group
                value={permissions.tool.type}
                onChange={(e) => handleTypeChange(e, 'tool')}
              >
                <Radio value="all">全部数据</Radio>
                <Radio value="specific">指定数据</Radio>
              </Radio.Group>
            </Form.Item>

            {permissions.tool.type === 'all' ? (
              <Form.Item label="权限" className="mt-4">
                <div className="flex space-x-4">
                  <Checkbox
                    checked={permissions.tool.allPermissions.view}
                    onChange={(e) => handleAllPermissionChange(e, 'tool', 'view')}
                  >
                    查看
                  </Checkbox>
                  <Checkbox
                    checked={permissions.tool.allPermissions.operate}
                    onChange={(e) => handleAllPermissionChange(e, 'tool', 'operate')}
                  >
                    操作
                  </Checkbox>
                </div>
              </Form.Item>
            ) : (
              <Table
                rowKey="id"
                columns={columns}
                dataSource={mockData.tool}
                pagination={false}
                className="mt-4"
              />
            )}
          </div>
        </div>
      ),
    },
  ];

  return (
    <Tabs
      activeKey={activeKey}
      onChange={setActiveKey}
      items={items}
      className="permission-rule-tabs"
    />
  );
};

export default PermissionRule;
