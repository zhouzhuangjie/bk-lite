import React from 'react';

interface IconProps {
  type: string;
  className?: string;
  style?: React.CSSProperties;
}

const Icon: React.FC<IconProps> = ({ type, className, style }) => (
  <svg className={`icon icon-${type} ${className}`} style={style} aria-hidden="true">
    <use xlinkHref={`#icon-${type}`} />
  </svg>
);

export default Icon;
