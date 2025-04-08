'use client';

import React from 'react';
import EntityList from '@/app/opspilot/components/entity-list';
import GenericModifyModal from '@/app/opspilot/components/generic-modify-modal';
import SkillCard from '@/app/opspilot/components/skill/skillCard';
import { Skill } from '@/app/opspilot/types/skill';

const SkillPage: React.FC = () => {
  return (
    <EntityList<Skill>
      endpoint="/opspilot/model_provider_mgmt/llm/"
      CardComponent={SkillCard}
      ModifyModalComponent={(props) => (
        <GenericModifyModal
          {...props}
          formType="skill"
        />
      )}
      itemTypeSingle="skill"
    />
  );
};

export default SkillPage;
