import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { Popover, Spin } from 'antd';
import { CaretDownFilled } from '@ant-design/icons';
import { useTranslation } from '@/utils/i18n';
import { usePermissions } from '@/context/permissions';
import { useClientData } from '@/context/client';
import UserInfo from '../user-info';
import Icon from '@/components/icon';
import styles from './index.module.scss';

const TopMenu = () => {
  const { t } = useTranslation();
  const { menus: menuItems } = usePermissions();
  const pathname = usePathname();
  const { clientData, loading } = useClientData();

  const sortedClientData = (clientData || []).sort((a, b) => {
    const forefrontId = 'ops-console';
    if (a.client_id === forefrontId && b.client_id !== forefrontId) {
      return -1;
    }
    if (a.client_id !== forefrontId && b.client_id === forefrontId) {
      return 1;
    }
    return 0;
  });

  const isConsole = process.env.NEXT_PUBLIC_IS_OPS_CONSOLE === 'true';

  const renderContent = loading ? (
    <div className="flex justify-center items-center h-32">
      <Spin tip="Loading..." />
    </div>
  ) : (
    <div className="grid grid-cols-3 gap-4 max-h-[350px] overflow-auto">
      {sortedClientData.map((app) => (
        <div
          key={app.name}
          className={`group flex flex-col items-center p-4 rounded-sm cursor-pointer ${styles.navApp}`}
          onClick={() => window.open(app.url, '_blank')}
        >
          <Icon
            type={app.client_id || 'yingyongxitongguanli'}
            className="text-2xl mb-1 transition-transform duration-300 transform group-hover:scale-125"
          />
          {app.name}
        </div>
      ))}
    </div>
  );

  return (
    <div className="z-30 flex flex-col grow-0 shrink-0 w-full basis-auto h-[56px] relative">
      <div className="flex items-center justify-between px-4 w-full h-full">
        <div className="flex items-center space-x-2">
          <Image src="/logo-site.png" className="block w-auto h-10" alt="logo" width={100} height={40} />
          <div className="font-medium">WeOps X</div>
          {!isConsole && (
            <Popover content={renderContent} title={t('common.appList')} trigger="hover">
              <div className={`flex items-center justify-center cursor-pointer rounded-[10px] px-3 py-2 ${styles.nav}`}>
                <Icon type="caidandaohang" className="mr-1" />
                <CaretDownFilled className={`text-sm ${styles.icons}`} />
              </div>
            </Popover>
          )}
        </div>
        <div className="flex items-center flex-shrink-0 space-x-4">
          <UserInfo />
        </div>
      </div>
      <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="flex items-center space-x-4">
          {menuItems
            .filter((item) => item.url && !item.isNotMenuItem)
            .map((item) => {
              const isActive = item.url === '/' ? pathname === '/' : pathname.startsWith(item.url);
              return (
                <Link key={item.url} href={item.url} prefetch={false} legacyBehavior>
                  <a className={`px-3 py-2 rounded-[10px] flex items-center ${styles.menuCol} ${isActive ? styles.active : ''}`}>
                    <Icon type={item.icon} className="mr-2 w-4 h-4" />
                    {item.title}
                  </a>
                </Link>
              );
            })}
        </div>
      </div>
    </div>
  );
};

export default TopMenu;
