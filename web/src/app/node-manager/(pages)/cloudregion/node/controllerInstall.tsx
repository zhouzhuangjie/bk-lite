'use client';
import React, {
  useEffect,
  useState,
  useRef,
  useCallback,
  useMemo,
} from 'react';
import { Spin, Button, Form, Select, Input, Segmented, message } from 'antd';
import type { FormInstance } from 'antd';
import useApiClient from '@/utils/request';
import { useTranslation } from '@/utils/i18n';
import { ModalRef, TableDataItem } from '@/app/node-manager/types';
import {
  ControllerInstallFields,
  ControllerInstallProps,
} from '@/app/node-manager/types/cloudregion';
import controllerInstallSyle from './index.module.scss';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useSearchParams } from 'next/navigation';
import {
  useInstallWays,
  OPERATE_SYSTEMS,
} from '@/app/node-manager/constants/cloudregion';
import CustomTable from '@/components/custom-table';
import BatchEditModal from './batchEditModal';
import {
  EditOutlined,
  PlusCircleOutlined,
  MinusCircleOutlined,
} from '@ant-design/icons';
import { cloneDeep, uniqueId } from 'lodash';
const { Option } = Select;
import useApiCloudRegion from '@/app/node-manager/api/cloudregion';
import useCloudId from '@/app/node-manager/hooks/useCloudid';
import ControllerTable from './controllerTable';
import ManualInstall from './manualInstall';
import { useUserInfoContext } from '@/context/userInfo';

const INFO_ITEM = {
  ip: null,
  organizations: [],
  port: null,
  username: null,
  password: null,
};

const ControllerInstall: React.FC<ControllerInstallProps> = ({
  cancel,
  config,
}) => {
  const { t } = useTranslation();
  const { isLoading } = useApiClient();
  const commonContext = useUserInfoContext();
  const { getnodelist, getPackages, installController } = useApiCloudRegion();
  const cloudId = useCloudId();
  const searchParams = useSearchParams();
  const [form] = Form.useForm();
  const instRef = useRef<ModalRef>(null);
  const tableFormRef = useRef<FormInstance>(null);
  const name = searchParams.get('name') || '';
  const [pageLoading, setPageLoading] = useState<boolean>(false);
  const [confirmLoading, setConfirmLoading] = useState<boolean>(false);
  const [installMethod, setInstallMethod] = useState<string>('remoteInstall');
  const [showInstallTable, setShowInstallTable] = useState<boolean>(false);
  const [nodeList, setNodeList] = useState<TableDataItem[]>([]);
  const [taskId, setTaskId] = useState<number | null>(null);
  const [sidecarVersionList, setSidecarVersionList] = useState<TableDataItem[]>(
    []
  );
  const [tableData, setTableData] = useState<TableDataItem[]>([
    {
      ...cloneDeep(INFO_ITEM),
      id: '0',
    },
  ]);
  const currentTableData = useRef<TableDataItem[]>([
    {
      ...cloneDeep(INFO_ITEM),
      id: '0',
    },
  ]);
  const installWays = useInstallWays();
  const groupList = (commonContext?.groups || []).map((item) => ({
    label: item.name,
    value: item.id,
  }));

  const tableColumns = useMemo(() => {
    const columns: any = [
      {
        title: t('node-manager.cloudregion.node.ipAdrress'),
        dataIndex: 'ip',
        width: 100,
        key: 'ip',
        render: (value: string, row: TableDataItem) => {
          return (
            <>
              <Form.Item name={`ip-${row.id}`}>
                <Input onBlur={(e) => handleInputBlur(e, row, 'ip')}></Input>
              </Form.Item>
            </>
          );
        },
      },
      {
        title: (
          <>
            {t('node-manager.cloudregion.node.organaziton')}
            <EditOutlined
              className="cursor-pointer ml-[10px] text-[var(--color-primary)]"
              onClick={() => batchEditModal('organizations')}
            />
          </>
        ),
        dataIndex: 'organizations',
        width: 100,
        key: 'organizations',
        render: (value: string, row: TableDataItem) => {
          return (
            <>
              <Form.Item name={`organizations-${row.id}`}>
                <Select
                  mode="multiple"
                  maxTagCount="responsive"
                  value={row.organizations}
                  onChange={(group) =>
                    handleSelectChange(group, row, 'organizations')
                  }
                >
                  {groupList.map((item) => (
                    <Option value={item.value} key={item.value}>
                      {item.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </>
          );
        },
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
      {
        title: t('common.actions'),
        dataIndex: 'action',
        width: 60,
        fixed: 'right',
        key: 'action',
        render: (value: string, row: TableDataItem, index: number) => {
          return (
            <>
              <Button
                type="link"
                icon={<PlusCircleOutlined />}
                onClick={() => addInfoItem(index)}
              ></Button>
              {!!index && (
                <Button
                  type="link"
                  icon={<MinusCircleOutlined />}
                  onClick={() => deleteInfoItem(row)}
                ></Button>
              )}
            </>
          );
        },
      },
    ];
    return installMethod === 'remoteInstall'
      ? columns
      : [...columns.slice(0, 3), columns[columns.length - 1]];
  }, [installMethod]);

  const isRemote = useMemo(() => {
    return installMethod === 'remoteInstall';
  }, [installMethod]);

  useEffect(() => {
    if (!isLoading) {
      initPage();
    }
  }, [isLoading]);

  useEffect(() => {
    form.resetFields();
  }, [name]);

  useEffect(() => {
    if (tableData?.length && tableFormRef.current) {
      const obj = tableFormRef.current.getFieldsValue() || {};
      setTimeout(() => {
        tableFormRef.current?.setFieldsValue(cloneDeep(obj));
      });
    }
  }, [tableData]);

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

  const batchEditModal = (field: string) => {
    instRef.current?.showModal({
      title: t('common.bulkEdit'),
      type: field,
      form: {},
    });
  };

  const changeCollectType = (id: string) => {
    setInstallMethod(id);
    form.setFieldsValue({
      work_node: null,
      sidecar_package: null,
      executor_package: null,
    });
    tableFormRef.current?.resetFields();
    const data = [
      {
        ...cloneDeep(INFO_ITEM),
        id: '0',
      },
    ];
    setTableData(data);
    currentTableData.current = data;
  };

  const addInfoItem = (index: number) => {
    const data = cloneDeep(currentTableData.current);
    data.splice(index + 1, 0, {
      ...cloneDeep(INFO_ITEM),
      id: uniqueId(),
    });
    currentTableData.current = data;
    setTableData(data);
  };

  const deleteInfoItem = (row: TableDataItem) => {
    const data = cloneDeep(currentTableData.current);
    const index = data.findIndex((item) => item.id === row.id);
    if (index != -1) {
      data.splice(index, 1);
      currentTableData.current = data;
      setTableData(data);
    }
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

  const handleSelectChange = (
    value: string,
    row: TableDataItem,
    key: string
  ) => {
    const data = cloneDeep(currentTableData.current);
    const index = data.findIndex((item) => item.id === row.id);
    if (index !== -1) {
      data[index][key] = value;
      currentTableData.current = data;
      setTableData(data);
    }
  };

  const initPage = () => {
    setPageLoading(true);
    Promise.all([getNodes(), getSidecarList()]).finally(() => {
      setPageLoading(false);
    });
  };

  const getNodes = async () => {
    const data = await getnodelist({
      cloud_region_id: Number(cloudId),
      operating_system: config.os,
    });
    setNodeList(data);
  };

  const getSidecarList = async () => {
    const data = await getPackages({ os: config.os });
    setSidecarVersionList(data);
  };

  const validateTableData = async () => {
    const data = cloneDeep(currentTableData.current);
    if (
      data.every((item) => Object.values(item).every((tex) => !!tex?.length))
    ) {
      return Promise.resolve();
    }
    return Promise.reject(new Error(t('common.valueValidate')));
  };

  const goBack = () => {
    cancel();
  };

  const handleCreate = () => {
    setConfirmLoading(false);
    form.validateFields().then((values) => {
      const nodes = currentTableData.current.map((item) => ({
        ip: item.ip,
        os: config.os,
        organizations: item.organizations,
        port: +item.port,
        username: item.username,
        password: item.password,
      }));
      const params = {
        cloud_region_id: +cloudId,
        nodes,
        work_node: values.work_node || '',
        package_id: values.sidecar_package || '',
      };
      create(params);
    });
  };

  const create = async (params: ControllerInstallFields) => {
    try {
      setConfirmLoading(true);
      const data = await installController(params);
      message.success(t('common.operationSuccessful'));
      setTaskId(data.task_id);
      setShowInstallTable(true);
    } catch {
      setTaskId(null);
    } finally {
      setConfirmLoading(false);
    }
  };

  const cancelInstall = useCallback(() => {
    goBack();
  }, []);

  return (
    <Spin spinning={pageLoading} className="w-full">
      {showInstallTable ? (
        <ControllerTable
          config={{
            taskId,
            type: 'controller',
            groupList,
          }}
          cancel={cancelInstall}
        ></ControllerTable>
      ) : (
        <div className={controllerInstallSyle.controllerInstall}>
          <div className={controllerInstallSyle.title}>
            <ArrowLeftOutlined
              className="text-[var(--color-primary)] text-[20px] cursor-pointer mr-[10px]"
              onClick={goBack}
            />
            <span>{t('node-manager.cloudregion.node.installController')}</span>
          </div>
          <div className={controllerInstallSyle.form}>
            <Form form={form} name="basic" layout="vertical">
              <Form.Item<ControllerInstallFields>
                required
                label={t('node-manager.cloudregion.node.installationMethod')}
              >
                <Form.Item name="install" noStyle>
                  <Segmented
                    options={installWays}
                    value={installMethod}
                    onChange={changeCollectType}
                  />
                </Form.Item>
                <div className={controllerInstallSyle.description}>
                  {t('node-manager.cloudregion.node.installWayDes')}
                </div>
              </Form.Item>
              {isRemote ? (
                <>
                  <Form.Item<ControllerInstallFields>
                    required
                    label={t('node-manager.cloudregion.node.defaultNode')}
                  >
                    <Form.Item
                      name="work_node"
                      noStyle
                      rules={[
                        { required: true, message: t('common.required') },
                      ]}
                    >
                      <Select
                        style={{
                          width: 300,
                        }}
                        showSearch
                        allowClear
                        placeholder={t('common.pleaseSelect')}
                      >
                        {nodeList.map((item) => (
                          <Option value={item.id} key={item.id}>
                            {item.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                    <div className={controllerInstallSyle.description}>
                      {t('node-manager.cloudregion.node.defaultNodeDes')}
                    </div>
                  </Form.Item>
                  <Form.Item<ControllerInstallFields>
                    required
                    label={t('node-manager.cloudregion.node.sidecarVersion')}
                  >
                    <Form.Item
                      name="sidecar_package"
                      noStyle
                      rules={[
                        { required: true, message: t('common.required') },
                      ]}
                    >
                      <Select
                        style={{
                          width: 300,
                        }}
                        showSearch
                        allowClear
                        placeholder={t('common.pleaseSelect')}
                      >
                        {sidecarVersionList.map((item) => (
                          <Option value={item.id} key={item.id}>
                            {item.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                    <div className={controllerInstallSyle.description}>
                      {t('node-manager.cloudregion.node.sidecarVersionDes')}
                    </div>
                  </Form.Item>
                  <Form.Item<ControllerInstallFields>
                    name="nodes"
                    label={t('node-manager.cloudregion.node.installInfo')}
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
                </>
              ) : (
                <ManualInstall
                  config={{
                    ...config,
                    sidecarVersionList,
                  }}
                />
              )}
            </Form>
          </div>
          <div className={controllerInstallSyle.footer}>
            {isRemote && (
              <Button
                type="primary"
                className="mr-[10px]"
                loading={confirmLoading}
                onClick={handleCreate}
              >
                {`${t('node-manager.cloudregion.node.toInstall')} (${tableData.length})`}
              </Button>
            )}
            <Button onClick={goBack}>{t('common.cancel')}</Button>
          </div>
        </div>
      )}
      <BatchEditModal
        ref={instRef}
        config={{
          systemList: OPERATE_SYSTEMS,
          groupList,
        }}
        onSuccess={handleBatchEdit}
      />
    </Spin>
  );
};

export default ControllerInstall;
