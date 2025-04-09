import { useCallback } from 'react';
import { message } from 'antd';
import { useKnowledgeApi } from '@/app/opspilot/api/knowledge';
import { useTranslation } from '@/utils/i18n';

const useSaveConfig = () => {
  const { t } = useTranslation();
  const { fetchPreviewData } = useKnowledgeApi();

  const validateConfig = useCallback((config: any) => {
    console.log('config', config);
    if (config.enable_semantic_chunk_parse && !config.semantic_chunk_parse_embedding_model) {
      message.error(t('knowledge.documents.selectSemanticModel'));
      return false;
    }
    if (config.enable_ocr_parse && !config.ocr_model) {
      message.error(t('knowledge.documents.selectOcrModel'));
      return false;
    }
    return true;
  }, []);

  const saveConfig = useCallback(async (config: any) => {
    if (!validateConfig(config)) {
      return false;
    }
    try {
      await fetchPreviewData(config);
      message.success(t('knowledge.documents.configSaved'));
      return true;
    } catch {
      message.error(t('knowledge.documents.preprocessFailed'));
      return false;
    }
  }, [validateConfig, fetchPreviewData]);

  return { saveConfig };
};

export default useSaveConfig;
