import useApiClient from '@/utils/request';

const useMonitorApi = () => {
  const { 
    get, 
    // post, 
    // del, 
    // put, 
    patch } = useApiClient();

  const getMonitorMetrics = async () => {
    return await get(`/monitor/api/metrics/`);
  };

  const getMonitorObject = async (params: any) => {
    return await get('/monitor/api/monitor_object/',{
      params
    });
  };

  const getMonitorAlert = async (params: any) => {
    return await get(`/monitor/api/monitor_alert//`,{
      params
    });
  };

  const getMonitorEventDetail = async (id: any, params: any) => {
    return await get(`/monitor/api/monitor_event/query/${id}/`,{
      params
    });
  };

  const getEventRaw = async (id: any) => {
    return await get(`/monitor/api/monitor_event/raw_data/${id}/`);
  }
  
  const getInstanceQuery = async (params: any) => {
    return await get(`/monitor/api/metrics_instance/query_range/`,{
      params
    })
  }

  const patchMonitorAlert = async (id:any, data: any) => {
    return await patch(`/monitor/api/monitor_alert/${id}/`, data);
  };



  return {
    getMonitorMetrics,
    getMonitorObject,
    getMonitorAlert,
    getMonitorEventDetail,
    getEventRaw,
    getInstanceQuery,
    patchMonitorAlert,
  }
  
}

export default useMonitorApi;