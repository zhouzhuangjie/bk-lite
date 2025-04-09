import React, { useState, useEffect, useRef } from 'react';
import { Switch, InputNumber, Select, Form, message, Radio, Button, Empty, Skeleton, List } from 'antd';
import styles from './modify.module.scss';
import Icon from '@/components/icon';
import { useTranslation } from '@/utils/i18n';
import { PreviewData, ModelOption, PreprocessStepProps } from '@/app/opspilot/types/knowledge';
import ContentDrawer from '@/components/content-drawer';
import useContentDrawer from '@/app/opspilot/hooks/useContentDrawer';
import { useKnowledgeApi } from '@/app/opspilot/api/knowledge';

const { Option } = Select;

const PreprocessStep: React.FC<PreprocessStepProps> = ({ onConfigChange, knowledgeSourceType, knowledgeDocumentIds, initialConfig }) => {
  const { t } = useTranslation();
  const { fetchSemanticModels, fetchOcrModels, fetchPreviewData } = useKnowledgeApi();
  const [formData, setFormData] = useState({
    chunkParsing: initialConfig?.chunkParsing ?? true,
    chunkSize: initialConfig?.chunkSize ?? 256,
    chunkOverlap: initialConfig?.chunkOverlap ?? 0,
    semanticChunkParsing: initialConfig?.semanticChunkParsing ?? false,
    semanticModel: initialConfig?.semanticModel ?? null,
    ocrEnhancement: initialConfig?.ocrEnhancement ?? false,
    ocrModel: initialConfig?.ocrModel ?? null,
    excelParsing: initialConfig?.excelParsing ?? false,
    excelParseOption: initialConfig?.excelParseOption ?? 'fullContent',
  });

  const [previewData, setPreviewData] = useState<PreviewData[]>([]);
  const [semanticModels, setSemanticModels] = useState<ModelOption[]>([]);
  const [ocrModels, setOcrModels] = useState<ModelOption[]>([]);
  const [loadingSemanticModels, setLoadingSemanticModels] = useState<boolean>(true);
  const [loadingOcrModels, setLoadingOcrModels] = useState<boolean>(true);
  const [loadingPreview, setLoadingPreview] = useState<boolean>(false);
  const initialConfigRef = useRef(initialConfig);
  const onConfigChangeRef = useRef(onConfigChange);
  const [isInitialConfigApplied, setIsInitialConfigApplied] = useState(false);

  const {
    drawerVisible,
    drawerContent,
    showDrawer,
    hideDrawer,
  } = useContentDrawer();

  const generateConfig = (preview: boolean) => ({
    preview,
    knowledge_source_type: knowledgeSourceType,
    knowledge_document_ids: preview ? [knowledgeDocumentIds[0]] : knowledgeDocumentIds,
    enable_general_parse: formData.chunkParsing,
    general_parse_chunk_size: formData.chunkSize,
    general_parse_chunk_overlap: formData.chunkOverlap,
    enable_semantic_chunk_parse: formData.semanticChunkParsing,
    semantic_chunk_parse_embedding_model: formData.semanticModel,
    enable_ocr_parse: formData.ocrEnhancement,
    ocr_model: formData.ocrModel,
    enable_excel_parse: formData.excelParsing,
    excel_header_row_parse: formData.excelParseOption === 'headerRow',
    excel_full_content_parse: formData.excelParseOption === 'fullContent',
  });

  const generateConfigRef = useRef(generateConfig);

  useEffect(() => {
    generateConfigRef.current = generateConfig;
  }, [formData, knowledgeSourceType, knowledgeDocumentIds]);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const [semanticData, ocrData] = await Promise.all([
          fetchSemanticModels(),
          fetchOcrModels()
        ]);

        setSemanticModels(semanticData);
        setOcrModels(ocrData);
        if (!isInitialConfigApplied && ocrData.length > 0) {
          setFormData((prevState) => ({
            ...prevState,
            ocrModel: ocrData.find((model: any) => model.enabled)?.id ?? ocrData[0].id,
          }));
        }
      } catch {
        message.error('Failed to fetch models');
      } finally {
        setLoadingSemanticModels(false);
        setLoadingOcrModels(false);
      }
    };

    fetchModels();
  }, []);

  useEffect(() => {
    if (
      !loadingSemanticModels &&
      !loadingOcrModels &&
      initialConfigRef.current &&
      Object.keys(initialConfigRef.current).length !== 0 &&
      !isInitialConfigApplied
    ) {
      setFormData({
        chunkParsing: initialConfigRef.current.chunkParsing,
        chunkSize: initialConfigRef.current.chunkSize,
        chunkOverlap: initialConfigRef.current.chunkOverlap,
        semanticChunkParsing: initialConfigRef.current.semanticChunkParsing,
        semanticModel: initialConfigRef.current.semanticModel,
        ocrEnhancement: initialConfigRef.current.ocrEnhancement,
        ocrModel: initialConfigRef.current.ocrModel,
        excelParsing: initialConfigRef.current.excelParsing,
        excelParseOption: initialConfigRef.current.excelParseOption,
      });
      setIsInitialConfigApplied(true);
      initialConfigRef.current = null;
    }
  }, [loadingSemanticModels, loadingOcrModels, isInitialConfigApplied]);

  useEffect(() => {
    const initConfigLen = initialConfigRef.current ? Object.keys(initialConfigRef.current).length : 0;
    if (isInitialConfigApplied && initialConfig && initConfigLen) {
      const config = generateConfigRef.current(false);
      onConfigChangeRef.current(config);
    }
    if (initialConfig && initConfigLen === 0) {
      const config = generateConfigRef.current(false);
      onConfigChangeRef.current(config);
    }
  }, [formData, isInitialConfigApplied]);

  const handleChange = (field: string, value: any) => {
    setFormData((prevState) => ({
      ...prevState,
      [field]: value,
    }));
  };

  const handlePreviewClick = async () => {
    if (formData.semanticChunkParsing && !formData.semanticModel) {
      message.error(t('knowledge.documents.selectSemanticError'));
      return;
    }
    if (formData.ocrEnhancement && !formData.ocrModel) {
      message.error(t('knowledge.documents.selectOcrError'));
      return;
    }
    setLoadingPreview(true);
    try {
      const config = generateConfigRef.current(true);
      const data = await fetchPreviewData(config);

      if (Array.isArray(data)) {
        setPreviewData(data.map((contxt, index) => ({
          id: index,
          content: contxt,
          characters: contxt.length
        })));
      } else {
        throw new Error(t('common.invalidData'));
      }
    } catch {
      message.error(t('common.fetchFailed'));
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleContentClick = (content: string) => {
    showDrawer(content);
  };

  return (
    <div className="flex justify-between">
      <div className={`flex-1 px-4 ${styles.config}`}>
        <h2 className="text-base font-semibold mb-3">{t('knowledge.documents.general')}</h2>
        <div className={`rounded-md p-4 mb-6 ${styles.configItem}`}>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-semibold">{t('knowledge.documents.chunkParsing')}</h3>
            <Switch size="small" checked={formData.chunkParsing} onChange={(checked) => handleChange('chunkParsing', checked)} />
          </div>
          <p className="mb-4 text-sm">{t('knowledge.documents.chunkParsingDesc')}</p>
          {formData.chunkParsing && (
            <Form layout="vertical">
              <Form.Item label={t('knowledge.documents.chunkSizeLabel')}>
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  value={formData.chunkSize}
                  onChange={(value) => handleChange('chunkSize', value)}
                  disabled={!formData.chunkParsing}
                  changeOnWheel
                />
              </Form.Item>
              <Form.Item label={t('knowledge.documents.chunkOverlap')}>
                <InputNumber
                  style={{ width: '100%' }}
                  min={0}
                  value={formData.chunkOverlap}
                  onChange={(value) => handleChange('chunkOverlap', value)}
                  disabled={!formData.chunkParsing}
                  changeOnWheel
                />
              </Form.Item>
            </Form>
          )}
        </div>
        <div className={`rounded-md p-4 mb-6 ${styles.configItem}`}>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-semibold">{t('knowledge.documents.semChunkParsing')}</h3>
            <Switch size="small" checked={formData.semanticChunkParsing} onChange={(checked) => handleChange('semanticChunkParsing', checked)} />
          </div>
          <p className="mb-4 text-sm">{t('knowledge.documents.semChunkParsingDesc')}</p>
          {formData.semanticChunkParsing && (
            <Form.Item label={t('common.model')}>
              <Select
                style={{ width: '100%' }}
                disabled={!formData.semanticChunkParsing}
                loading={loadingSemanticModels}
                value={formData.semanticModel}
                onChange={(value) => handleChange('semanticModel', value)}
              >
                {semanticModels.map((model) => (
                  <Option key={model.id} value={model.id} disabled={!model.enabled}>{model.name}</Option>
                ))}
              </Select>
            </Form.Item>
          )}
        </div>
        <div className={`rounded-md p-4 mb-6 ${styles.configItem}`}>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-semibold">{t('knowledge.documents.ocrEnhancement')}</h3>
            <Switch size="small" checked={formData.ocrEnhancement} onChange={(checked) => handleChange('ocrEnhancement', checked)} />
          </div>
          <p className="mb-4 text-sm">{t('knowledge.documents.ocrEnhancementDesc')}</p>
          {formData.ocrEnhancement && (
            <Form.Item label={`OCR ${t('common.model')}`}>
              <Select
                style={{ width: '100%' }}
                disabled={!formData.ocrEnhancement}
                loading={loadingOcrModels}
                value={formData.ocrModel}
                onChange={(value) => handleChange('ocrModel', value)}
              >
                {ocrModels.map((model) => (
                  <Option key={model.id} value={model.id} disabled={!model.enabled}>{model.name}</Option>
                ))}
              </Select>
            </Form.Item>
          )}
        </div>
        <h2 className="text-base font-semibold mb-3">{t('knowledge.documents.advanceSettings')}</h2>
        <div className={`rounded-md p-4 mb-6 ${styles.configItem}`}>
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-sm font-semibold">{t('knowledge.documents.excelParsing')}</h3>
            <Switch size="small" checked={formData.excelParsing} onChange={(checked) => handleChange('excelParsing', checked)} />
          </div>
          <p className="mb-4 text-sm">{t('knowledge.documents.excelParsingDesc')}</p>
          {formData.excelParsing && (
            <Radio.Group
              onChange={(e) => handleChange('excelParseOption', e.target.value)}
              value={formData.excelParseOption}
              disabled={!formData.excelParsing}
            >
              <Radio value="headerRow">{t('knowledge.documents.headerRow')}</Radio>
              <Radio value="fullContent">{t('knowledge.documents.fullContent')}</Radio>
            </Radio.Group>
          )}
        </div>
      </div>
      <div className="flex-1 px-4">
        <div className="flex justify-between">
          <h2 className="text-base font-semibold mb-3">{t('knowledge.documents.preview')}</h2>
          <Button type="primary" size="small" onClick={handlePreviewClick} loading={loadingPreview}>{t('knowledge.documents.viewChunk')}</Button>
        </div>
        {loadingPreview ? (
          <List
            itemLayout="vertical"
            dataSource={[1, 2, 3]}
            renderItem={() => (
              <List.Item>
                <Skeleton active />
              </List.Item>
            )}
          />
        ) : previewData.length > 0 ? (
          previewData.map((item) => (
            <div key={item.id} className={`rounded-md p-4 mb-3 ${styles.previewItem}`} onClick={() => handleContentClick(item.content)}>
              <div className="flex justify-between items-center mb-2">
                <span className={`text-xs flex items-center ${styles.number}`}>#{item.id.toString().padStart(3, '0')}</span>
                <span className="flex items-center stext-sm"><Icon type="zifu" className="text-xl pr-1" />{item.characters} {t('knowledge.documents.characters')}</span>
              </div>
              <div>
                <p>{item.content}</p>
              </div>
            </div>
          ))
        ) : (
          <Empty description={t('common.noResult')} />
        )}
      </div>
      <ContentDrawer
        visible={drawerVisible}
        onClose={hideDrawer}
        content={drawerContent}
      />
    </div>
  );
};

export default PreprocessStep;
