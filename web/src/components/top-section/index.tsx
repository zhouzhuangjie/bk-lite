import React from 'react';
import Icon from '@/components/icon'
import EllipsisWithTooltip from '@/components/ellipsis-with-tooltip'

interface TopSectionProps {
  title: string;
  content: string;
  iconType?: string;
}

const TopSection: React.FC<TopSectionProps> = ({ title, content, iconType }) => (
  <div className="p-4 rounded-md w-full h-[80px] bg-[var(--color-bg)] flex items-center">
    {iconType && (
      <div>
        <Icon type={iconType} className="mr-2 text-6xl" />
      </div>
    )}
    <div className="flex-1 overflow-hidden">
      <h2 className="text-base font-semibold mb-2">{title}</h2>
      <EllipsisWithTooltip className="text-xs text-[var(--color-text-3)] whitespace-nowrap overflow-hidden text-ellipsis" text={content} />
    </div>
  </div>
);

export default TopSection;
