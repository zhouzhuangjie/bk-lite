'use client';

import React from 'react';
import CommonProvider from '@/app/cmdb/context/common';

export const CMDBRootLayout = ({ children }: { children: React.ReactNode }) => {
  return <CommonProvider>{children}</CommonProvider>;
};

export default CMDBRootLayout;
