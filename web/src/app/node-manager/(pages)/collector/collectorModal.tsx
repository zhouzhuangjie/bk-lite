import React, { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react"
import { ModalRef, ModalSuccess, TableDataItem } from "@/app/node-manager/types";
import { Form, Button, Input, Select, Upload, message, Popconfirm } from "antd";
import { CloudUploadOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { FormInstance } from "antd/lib";
import { useTranslation } from "@/utils/i18n";
import OperateModal from "@/components/operate-modal";
import useApiCollector from "@/app/node-manager/api/collector";
import { cloneDeep } from "lodash";
const { TextArea } = Input;
const { Dragger } = Upload;
const initData = {
  name: '',
  system: '',
  description: '',
  service_type: '',
  executable_path: '',
  execute_parameters: '',
}

const CollectorModal = forwardRef<ModalRef, ModalSuccess>(({ onSuccess }, ref) => {
  const { t } = useTranslation();
  const {
    uploadPackage,
    addCollector,
    deleteCollector,
    editCollecttor,
  } = useApiCollector();
  const formRef = useRef<FormInstance>(null);
  const [form] = Form.useForm();
  const [title, setTitle] = useState<string>('editCollector');
  const [type, setType] = useState<string>('edit');
  const [id, setId] = useState<string>('');
  const [key, setKey] = useState<string>('');
  const [visible, setVisible] = useState<boolean>(false);
  const [confirmLoading, setConfirmLoading] = useState<boolean>(false);
  const [formData, setFormData] = useState<TableDataItem>(initData);
  const [fileList, setFileList] = useState<any>([]);
  //需要二次弹窗确定的类型
  const Popconfirmarr = ["delete"];

  useImperativeHandle(ref, () => ({
    showModal: ({ type, form, title, key }) => {
      const info = cloneDeep(form) as TableDataItem;
      const { name, tagList, description } = form as TableDataItem;
      setKey(key as string);
      setId(form?.id as string);
      setType(type);
      setTitle(title as string);
      setVisible(true);
      if (type !== 'add') {
        info.name = name || "";
        info.system = tagList?.length ? tagList[0] : 'windows';
        info.description = description || '--';
      } else {
        info.system = "windows";
        info.name = "";
        info.description = "";
      }
      setFormData(info);
    }
  }));

  useEffect(() => {
    formRef.current?.resetFields();
    formRef.current?.setFieldsValue(formData);
  }, [formRef, formData])

  const handleCancel = () => {
    formRef.current?.resetFields();
    setVisible(false);
  };

  const errorCatch = (error: any) => {
    message.error(error.code);
    setConfirmLoading(false);
  }

  const onSubmit = () => {
    if (Popconfirmarr.includes(type)) {
      return;
    }
    setConfirmLoading(true);
    formRef.current?.validateFields().then((values) => {
      const param = {
        id: id || `${values.name}_${values.system}`,
        name: values.name,
        service_type: formData.service_type || 'exec',
        node_operating_system: values.system,
        introduction: values.description,
        executable_path: formData.executable_path || 'text/',
        execute_parameters: formData.execute_parameters || 'text',
      };
      if (type === 'add') {
        addCollector(param).then(() => {
          setConfirmLoading(false);
          setVisible(false);
          message.success(t('common.addSuccess'));
          onSuccess();
        }).catch(errorCatch)
      } else if (type === 'edit') {
        editCollecttor(param).then(() => {
          setConfirmLoading(false);
          setVisible(false);
          message.success(t('common.updateSuccess'));
          onSuccess();
        }).catch(errorCatch)
      } else if (type === 'upload') {
        handleUpload(values);
      }
    }).catch(() => {
      setConfirmLoading(false);
    });
  };

  const handleChange: UploadProps['onChange'] = ({ fileList }) => {
    setFileList(fileList);
  };

  const handleUpload = async (values: any) => {
    const file = fileList.length ? fileList[0] : '';
    if (file) {
      const fd = new FormData();
      fd.append('file', file.originFileObj);
      const params = {
        name: file.name,
        os: formData.system,
        type: key,
        version: values.version,
        object: formData.name,
        file: file.originFileObj
      };
      Object.entries(params).forEach(([k, v]) => {
        fd.append(k, v);
      });
      uploadPackage(params).then(() => {
        setConfirmLoading(false);
        message.success(t('node-manager.collector.uploadSuccess'));
        setVisible(false);
      });
    }
  }

  const props: UploadProps = {
    name: 'file',
    multiple: false,
    maxCount: 1,
    fileList: fileList,
    onChange: handleChange,
    beforeUpload: () => false
  };

  const validateUpload = async (_: any, value: any) => {
    if (!value) {
      return Promise.reject(new Error(t('common.inputRequired')));
    }
    return Promise.resolve();
  };

  //删除确认的弹窗
  const deleteConfirm = () => {
    setConfirmLoading(true);
    formRef.current?.validateFields().then(() => {
      deleteCollector({ id })
        .then(() => {
          setConfirmLoading(false);
          message.success('common.delSuccess');
          setVisible(false);
          onSuccess();
        })
        .catch(() => {
          setConfirmLoading(false);
        })
    })
  };

  const normFile = (e: any) => {
    console.log('Upload event:', e);
    if (Array.isArray(e)) {
      return e;
    }
    return e && e.fileList;
  };

  return (
    <div>
      <OperateModal
        title={t(`node-manager.collector.${title}`)}
        open={visible}
        onCancel={handleCancel}
        footer={
          <div>
            {
              Popconfirmarr.includes(type) ?
                <Popconfirm
                  title={t(`node-manager.collector.${type}`)}
                  description={t(`node-manager.collector.${type}Info`)}
                  okText={t("common.confirm")}
                  cancelText={t("common.cancel")}
                  onConfirm={deleteConfirm}
                >
                  <Button
                    className="mr-[10px]"
                    type="primary"
                    loading={confirmLoading}
                    danger
                  >
                    {t("common.delete")}
                  </Button>
                </Popconfirm>
                : <Button type="primary" className="mr-[10px]" loading={confirmLoading} onClick={onSubmit}>{t('common.confirm')}</Button>
            }
            <Button onClick={handleCancel}>{t('common.cancel')}</Button>
          </div>
        }
      >
        <Form
          ref={formRef}
          form={form}
          initialValues={formData}
          layout="vertical"
        >
          {(['edit', 'add', 'delete'].includes(type)) && (<>
            <Form.Item<any>
              label={t('common.name')}
              name="name"
              rules={[{ required: true, message: t('common.inputRequired') }]}
            >
              <Input disabled={type === 'delete'} />
            </Form.Item>
            <Form.Item<any>
              label={t('node-manager.cloudregion.Configuration.system')}
              name="system"
              rules={[{ required: true, message: t('common.inputRequired') }]}
            >
              <Select
                disabled={type !== 'add'}
                options={[
                  { value: 'linux', label: 'Linux' },
                  { value: 'windows', label: 'Windows' }
                ]}>
              </Select>
            </Form.Item>
            <Form.Item<any>
              label={t('node-manager.cloudregion.Configuration.description')}
              name="description"
              rules={[{ required: true, message: t('common.inputRequired') }]}
            >
              <TextArea disabled={type === 'delete'} />
            </Form.Item>
          </>)}
          {type === 'upload' && (<>
            <Form.Item<any>
              label={t('node-manager.collector.version')}
              name="version"
              rules={[{ required: true, message: t('common.inputRequired') }]}
            >
              <Input />
            </Form.Item>
            <Form.Item<any>
              label={t('node-manager.collector.importFile')}
              name="upload"
              valuePropName="fileList"
              getValueFromEvent={normFile}
              rules={[{ required: true, validator: validateUpload }]}
            >
              <Dragger {...props}>
                <p className="ant-upload-drag-icon">
                  <CloudUploadOutlined />
                </p>
                <p className="flex justify-center content-center items-center">{t('common.uploadText')}<Button type="link">点击上传</Button></p>
              </Dragger>
            </Form.Item>
          </>)}
        </Form>
      </OperateModal>
    </div>
  )
});

CollectorModal.displayName = 'CollectorModal';
export default CollectorModal;