'use client';

import React from 'react';
import EntityCard from '@/app/opspilot/components/entity-card';
import { Studio } from '@/app/opspilot/types/studio';

interface StudioCardProps extends Studio {
  index: number;
  onMenuClick: (action: string, studio: Studio) => void;
}

const StudioCard: React.FC<StudioCardProps> = (props) => {
  const { id, name, introduction, created_by, team_name, team, index, llm_model_name, onMenuClick } = props;
  const iconTypeMapping: [string, string] = ['jiqirenjiaohukapian', 'jiqiren'];

  return (
    <EntityCard
      id={id}
      name={name}
      introduction={introduction}
      created_by={created_by}
      team_name={team_name}
      team={team}
      index={index}
      modelName={llm_model_name}
      onMenuClick={onMenuClick}
      redirectUrl="/opspilot/skill/detail"
      iconTypeMapping={iconTypeMapping}
    />
  );
};

export default StudioCard;
