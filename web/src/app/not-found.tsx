'use client';
import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useTranslation } from '@/utils/i18n';

const NotFoundPage = () => {
  const { t } = useTranslation();
  return (
    <div className="flex items-center justify-center text-center w-[850px] m-auto">
      <div className="w-1/2 flex flex-col items-start">
        <h1 className="text-[22px] md:text-[calc(4rem+2vw)] font-mono uppercase font-bold contents">404</h1>
        <p className="text-base text-[var(--color-text-3)] mb-10 mt-6">
          {t('common.notFound')}
        </p>
        <Link legacyBehavior href="/" passHref>
          <a className="text-[var(--color-primary)] hover:underline text-base">{t('common.backToHome')}</a>
        </Link>
      </div>

      <div className="w-1/2 flex justify-center mt-0">
        <Image
          src="/page-tip.gif"
          alt="404 Not Found"
          width={400}
          height={400}
          className="rounded"
        />
      </div>
    </div>
  );
};

export default NotFoundPage;
