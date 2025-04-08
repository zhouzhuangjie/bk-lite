'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Breadcrumb, Button, Steps, message, Spin } from 'antd';
import LocalFileUpload from './localFileUpload';
import WebLinkForm from './webLinkForm';
import CustomTextForm from './customTextForm';
import PreprocessStep from './preprocessStep';
import Icon from '@/components/icon'
import useSaveConfig from '@/app/opspilot/hooks/useSaveConfig';
import { useTranslation } from '@/utils/i18n';
import { useKnowledgeApi } from '@/app/opspilot/api/knowledge';

const { Step } = Steps;

const KnowledgeModifyPage = () => {
  const { t } = useTranslation();
  const searchParams = useSearchParams();
  const router = useRouter();
  const type = searchParams ? searchParams.get('type') : null;
  const id = searchParams ? searchParams.get('id') : null;
  const name = searchParams ? searchParams.get('name') : null;
  const desc = searchParams ? searchParams.get('desc') : null;
  const { saveConfig } = useSaveConfig();
  const { 
    updateDocumentBaseInfo, 
    createWebPageKnowledge, 
    createFileKnowledge, 
    createManualKnowledge, 
    getDocumentDetail 
  } = useKnowledgeApi();
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [isStepValid, setIsStepValid] = useState<boolean>(false);
  const [fileList, setFileList] = useState<File[]>([]);
  const [documentIds, setDocumentIds] = useState<number[]>([]);
  const [preprocessConfig, setPreprocessConfig] = useState<any>(null);
  const [webLinkData, setWebLinkData] = useState<{ name: string, link: string, deep: number }>({ name: '', link: '', deep: 1 });
  const [manualData, setManualData] = useState<{ name: string, content: string }>({ name: '', content: '' });
  const [pageLoading, setPageLoading] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [confirmLoading, setConfirmLoading] = useState<boolean>(false);
  const [config, setConfig] = useState(null);
  const [isUpdate, setIsUpdate] = useState<boolean>(false);

  const formRef = useRef<any>(null);

  useEffect(() => {
    const configParam = searchParams ? searchParams.get('config') : null;
    const idParam = searchParams ? searchParams.get('documentId') : null;
    if (idParam && configParam) {
      setCurrentStep(1);
      setIsUpdate(true);
      setDocumentIds([Number(idParam)]);
      setConfig(JSON.parse(configParam));
    }
    setPageLoading(false);
  }, [searchParams]);

  const sourceTypeToDisplayText: { [key: string]: string } = {
    file: t('knowledge.localFile'),
    web_page: t('knowledge.webLink'),
    manual: t('knowledge.cusText'),
  };

  const handleNext = async () => {
    setLoading(true);

    if (currentStep === 0) {
      if (type === 'web_page') {
        try {
          await formRef.current?.validateFields();
          const params = {
            name: webLinkData.name,
            url: webLinkData.link,
            max_depth: webLinkData.deep,
          };
          if (documentIds.length) {
            await updateDocumentBaseInfo(documentIds[0], params);
          } else {
            const data = await createWebPageKnowledge(id, params);
            setDocumentIds([data]);
          }
          message.success(t('knowledge.documents.webLinkSaveSuccess'));
        } catch {
          message.error(t('knowledge.documents.webLinkSaveFail'));
          setLoading(false);
          return;
        }
      } else if (type === 'file') {
        try {
          const formData = new FormData();
          formData.append('knowledge_base_id', id as string);
          fileList.forEach(file => formData.append('files', file));

          const data = await createFileKnowledge(formData);
          setDocumentIds(data);
          message.success(t('knowledge.documents.fileUploadSuccess'));
        } catch {
          message.error(t('knowledge.documents.fileUploadFailed'));
          setLoading(false);
          return;
        }
      } else if (type === 'manual') {
        try {
          const params = {
            name: manualData.name,
            content: manualData.content,
          };
          if (documentIds.length) {
            await updateDocumentBaseInfo(documentIds[0], params);
          } else {
            const data = await createManualKnowledge(id, params);
            setDocumentIds([data]);
          }
          message.success(t('knowledge.documents.manualDataSaveSuccess'));
        } catch {
          message.error(t('knowledge.documents.manualDataSaveFailed'));
          setLoading(false);
          return;
        }
      }
    } else if (currentStep === 1) {
      const success = await saveConfig(preprocessConfig);
      if (!success) {
        setLoading(false);
        return;
      }
    }
    setCurrentStep(currentStep + 1);
    setLoading(false);
  };

  const handleConfirm = async () => {
    setConfirmLoading(true);
    await saveConfig({
      ...(preprocessConfig as object),
      is_save_only: true,
    });
    setCurrentStep(currentStep + 1);
    setConfirmLoading(false);
  }

  const handlePrevious = async () => {
    if (isUpdate && (type === 'web_page' || type === 'manual')) {
      const data = await getDocumentDetail(documentIds[0]);
      if (type === 'web_page') {
        setWebLinkData({
          name: data.name,
          link: data.url,
          deep: data.max_depth,
        });
      } else if (type === 'manual') {
        setManualData({
          name: data.name,
          content: data.content,
        });
      }
    }
    setCurrentStep(currentStep - 1);
  };

  const handleValidationChange = useCallback((isValid: boolean) => {
    setIsStepValid(isValid);
  }, []);

  const handleFileChange = useCallback((files: File[]) => {
    setFileList(files);
    setIsStepValid(files.length > 0);
  }, []);

  const handlePreprocessConfigChange = useCallback((config: any) => {
    setPreprocessConfig(config);
    setIsStepValid(true);
  }, []);

  const handleWebLinkDataChange = useCallback((data: { name: string, link: string, deep: number }) => {
    setWebLinkData(data);
  }, []);

  const handleManualDataChange = useCallback((data: { name: string, content: string }) => {
    setManualData(data);
  }, []);

  const handleDone = () => {
    router.push(`/opspilot/knowledge/detail/documents?id=${id}&name=${name}&desc=${desc}&type=${type}`);
  };

  const handleToTesting = () => {
    router.push(`/opspilot/knowledge/detail/testing?id=${id}&name=${name}&desc=${desc}`);
  };

  const renderStepContent = () => {
    switch (type) {
      case 'file':
        return <LocalFileUpload onFileChange={handleFileChange} initialFileList={fileList} />;
      case 'web_page':
        return <WebLinkForm ref={formRef} initialData={webLinkData} onFormChange={handleValidationChange} onFormDataChange={handleWebLinkDataChange} />;
      case 'manual':
        return <CustomTextForm initialData={manualData} onFormChange={handleValidationChange} onFormDataChange={handleManualDataChange} />;
      default:
        return <LocalFileUpload onFileChange={handleFileChange} initialFileList={fileList} />;
    }
  };

  const steps = [
    {
      title: t('knowledge.choose'),
      content: renderStepContent(),
    },
    {
      title: t('knowledge.preprocess'),
      content: <PreprocessStep
        knowledgeSourceType={type}
        knowledgeDocumentIds={documentIds}
        onConfigChange={handlePreprocessConfigChange}
        initialConfig={config || {}} />,
    },
    {
      title: t('knowledge.finish'),
      content: (
        <div className="flex flex-col items-center">
          <Icon className="text-8xl mb-2" type="finish" />
          <p>{t('knowledge.finishTip')}</p>
          <p>
            <span className='text-blue-500 cursor-pointer' onClick={handleDone}>{t('knowledge.backToList')}</span>
            <span> {t('knowledge.or')} </span>
            <span className='text-blue-500 cursor-pointer' onClick={handleToTesting}>{t('knowledge.goToTesting')}</span>
          </p>
        </div>
      ),
    },
  ];

  return (
    <div>
      <Breadcrumb>
        <Breadcrumb.Item>{t('knowledge.menu')}</Breadcrumb.Item>
        <Breadcrumb.Item>{type && sourceTypeToDisplayText[type]}</Breadcrumb.Item>
        <Breadcrumb.Item>{isUpdate ? t('common.update') : t('common.create')}</Breadcrumb.Item>
      </Breadcrumb>
      <div className="px-7 py-5">
        {pageLoading ? (
          <div className="flex items-center justify-center h-full">
            <Spin />
          </div>
        ) : (
          <div>
            <Steps className="px-16 py-8" current={currentStep}>
              {steps.map((step, index) => (
                <Step key={index} title={step.title} />
              ))}
            </Steps>
            <div className="steps-content" style={{ marginTop: 24 }}>
              {steps[currentStep].content}
            </div>
          </div>
        )}
        <div className="fixed bottom-10 right-20 z-50 flex space-x-2">
          {currentStep > 0 && currentStep < steps.length - 1 && type !== 'file' && (
            <Button onClick={handlePrevious}>
              {t('common.pre')}
            </Button>
          )}
          {
            currentStep === 1  && isUpdate && (
              <Button type="primary" onClick={handleConfirm} disabled={!isStepValid} loading={confirmLoading}>
                {t('common.confirm')}
              </Button>
            )
          }
          {currentStep < steps.length - 1 && (
            <Button type="primary" onClick={handleNext} disabled={!isStepValid} loading={loading}>
              {currentStep === 1 ? t('knowledge.finish') : t('common.next')}
            </Button>
          )}
          {currentStep === steps.length - 1 && (
            <Button type="primary" onClick={handleDone}>
              {t('common.done')}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeModifyPage;
