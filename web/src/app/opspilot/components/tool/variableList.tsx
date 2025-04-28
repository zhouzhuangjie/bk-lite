import React from 'react';
import { Button, Input } from 'antd';
import { useTranslation } from '@/utils/i18n';
import { PlusOutlined, MinusOutlined } from '@ant-design/icons';

interface VariableListProps {
  value?: string[];
  onChange?: (value: string[]) => void;
}

const VariableList: React.FC<VariableListProps> = ({ value = [], onChange }) => {
  const { t } = useTranslation();
  const variables = value.length > 0 ? value : [''];

  const handleAdd = () => {
    const updatedVariables = [...variables, ''];
    onChange?.(updatedVariables);
  };

  const handleDelete = (index: number) => {
    const updatedVariables = variables.filter((_, i) => i !== index);
    onChange?.(updatedVariables);
  };

  const handleChange = (newValue: string, index: number) => {
    const updatedVariables = [...variables];
    updatedVariables[index] = newValue;
    onChange?.(updatedVariables);
  };

  return (
    <div className="space-y-2">
      {variables.map((variable, index) => (
        <div key={index} className="flex items-center space-x-2">
          <Input
            value={variable}
            onChange={(e) => handleChange(e.target.value, index)}
            placeholder={`${t('common.inputMsg')}${t('tool.variables')}`}
            className="flex-1"
          />
          <Button
            size="small"
            shape="circle"
            icon={<PlusOutlined />}
            onClick={handleAdd}
            className="flex-shrink-0"
          />
          <Button
            size="small"
            shape="circle"
            icon={<MinusOutlined />}
            onClick={() => handleDelete(index)}
            className={`flex-shrink-0 ${index === 0 ? 'invisible' : ''}`}
          />
        </div>
      ))}
    </div>
  );
};

export default VariableList;
