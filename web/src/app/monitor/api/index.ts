import useApiClient from '@/utils/request';

const useMonitorApi = () => {
  const {
    get,
    post,
    del,
    // put, 
    patch } = useApiClient();

  const getMonitorMetrics = async (params?: any) => {
    return await get(`/monitor/api/metrics/`, {
      params
    });
  };

  const getMetricsGroup = async (params?: any) => {
    return await get(`/monitor/api/metrics_group/`, {
      params
    });
  };

  const getMonitorObject = async (params?: any) => {
    return await get('/monitor/api/monitor_object/', {
      params
    });
  };

  const getMonitorAlert = async (params?: any) => {
    return await get(`/monitor/api/monitor_alert//`, {
      params
    });
  };

  const getMonitorEventDetail = async (id?: any, params?: any) => {
    return await get(`/monitor/api/monitor_event/query/${id}/`, {
      params
    });
  };

  const getEventRaw = async (id?: any) => {
    return await get(`/monitor/api/monitor_event/raw_data/${id}/`);
  };

  const getInstanceQuery = async (params?: any) => {
    return await get(`/monitor/api/metrics_instance/query_range/`, {
      params
    })
  };

  const getInstanceList = async (objectId?: any, params?: any) => {
    return await get(`/monitor/api/monitor_instance/${objectId}/list/`, {
      params
    });
  };

  const getInstanceSearch = async (objectId: any, data: any) => {
    return await post(`/monitor/api/monitor_instance/${objectId}/search/`, data)
  };

  const getInstanceGroupRule = async (params?: any) => {
    return await get(`/monitor/api/monitor_instance_group_rule/`, {
      params
    });
  };

  const getInstanceChildConfig = async (data: any) => {
    return await post(`/monitor/api/node_mgmt/get_instance_child_config/`, data)
  };

  const getInstanceQueryParams = async (name: string, params: any) => {
    return await get(`/monitor/api/monitor_instance/query_params_enum/${name}/`, {
      params
    });
  };

  const getMonitorPolicy = async (id?: any, params?: any) => {
    return await get(`/monitor/api/monitor_policy/${id}`, {
      params
    });
  };

  const getPolicyTemplate = async (params?: any) => {
    return await post('/monitor/api/monitor_policy/template/', params)
  };

  const getMonitorPlugin = async (params?: any) => {
    return await get('/monitor/api/monitor_plugin/', {
      params
    })
  };

  const getMonitorNodeList = async (data: any) => {
    return await post('/monitor/api/node_mgmt/nodes/', data)
  };

  const getSystemChannelList = async () => {
    return await get('/monitor/api/system_mgmt/search_channel_list/');
  };

  const patchMonitorAlert = async (id: any, data: any) => {
    return await patch(`/monitor/api/monitor_alert/${id}/`, data);
  };

  const patchMonitorPolicy = async (id: number, data: any) => {
    return await patch(`/monitor/api/monitor_policy/${id}/`, data)
  };

  const updateInstanceChildConfig = async (data: any) => {
    return await post('/monitor/api/node_mgmt/update_instance_child_config/', data)
  };

  const updateMonitorObject = async (data: any) => {
    return await post(`/monitor/api/monitor_object/order/`, data);
  };

  const importMonitorPlugin = async (data: any) => {
    return await post(`/monitor/api/monitor_plugin/import/`, data)
  };

  const updateMetricsGroup = async (data: any) => {
    return await post('/monitor/api/metrics_group/set_order/', data);
  };

  const updateMonitorMetrics = async (data: any) => {
    return await post('/monitor/api/metrics/set_order/', data);
  };

  const updateNodeChildConfig = async (data: any) => {
    return await post('/monitor/api/node_mgmt/batch_setting_node_child_config/', data);
  };

  const checkMonitorInstance = async (id: any, data: any) => {
    return await post(`/monitor/api/monitor_instance/${id}/check_monitor_instance/`, data)
  };

  const deleteMonitorPolicy = async (id: number | string) => {
    return await del(`/monitor/api/monitor_policy/${id}/`);
  };

  const deleteInstanceGroupRule = async (id: number | string) => {
    return await del(`/monitor/api/monitor_instance_group_rule/${id}/`);
  };

  const deleteMonitorInstance = async (data: any) => {
    return await post(`/monitor/api/monitor_instance/remove_monitor_instance/`, data)
  };

  const deleteMonitorMetrics = async (id: any) => {
    return await del(`/monitor/api/metrics/${id}/`);
  };

  const deleteMetricsGroup = async (id: any) => {
    return await del(`/monitor/api/metrics_group/${id}/`);
  };



  return {
    getMonitorMetrics,
    getMetricsGroup,
    getMonitorObject,
    getMonitorAlert,
    getMonitorEventDetail,
    getEventRaw,
    getInstanceQuery,
    getInstanceList,
    getInstanceSearch,
    getInstanceGroupRule,
    getInstanceChildConfig,
    getInstanceQueryParams,
    getMonitorPolicy,
    getPolicyTemplate,
    getSystemChannelList,
    getMonitorPlugin,
    getMonitorNodeList,
    patchMonitorAlert,
    patchMonitorPolicy,
    updateInstanceChildConfig,
    updateMonitorObject,
    importMonitorPlugin,
    updateMetricsGroup,
    updateMonitorMetrics,
    updateNodeChildConfig,
    checkMonitorInstance,
    deleteMonitorPolicy,
    deleteInstanceGroupRule,
    deleteMonitorInstance,
    deleteMonitorMetrics,
    deleteMetricsGroup,
  }

}

export default useMonitorApi;