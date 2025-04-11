import { useEffect, useState } from 'react';

const useCloudId = () => {
  const [cloudid, setCloudid] = useState<string>('1');

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const id = searchParams.get('cloud_region_id');
    if (typeof id === 'string') {
      setCloudid(id);
    }
  }, []);

  return cloudid;
};

export default useCloudId;
