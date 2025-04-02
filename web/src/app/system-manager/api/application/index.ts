import useApiClient from '@/utils/request';
export const useRoleApi = () => {
  const { get, post } = useApiClient();
  const getRoles = async (params: any) => {
    return await post('/system_mgmt/role/search_role_list/', params);
  }
  const addRole = async (params: any) => {
    return await post('/system_mgmt/role/create_role/', params);
  }
  const updateRole = async (params: any) => {
    return await post('/system_mgmt/role/update_role/', params);
  }
  const deleteRole = async (params: any) => {
    return await post('/system_mgmt/role/delete_role/', params);
  }
  const getUsersByRole = async (params: any) => {
    return await get('/system_mgmt/role/search_role_users/', params);
  }
  const getAllUser = async () => {
    return await get('/system_mgmt/user/user_all/');
  }
  const getRoleMenus = async (params: any) => {
    return await get('/system_mgmt/role/get_role_menus/', params);
  }
  const getAllMenus = async (params: any) => {
    return await get('/system_mgmt/role/get_all_menus/', params);
  }
  const setRoleMenus = async (params: any) => {
    return await post('/system_mgmt/role/set_role_menus/', params);
  }
  const addUser = async (params: any) => {
    return await post('/system_mgmt/role/add_user/', params);
  }
  const deleteUser = async (params: any) => {
    return await post('/system_mgmt/role/delete_user/', params);
  }
  return {
    getRoles,
    addRole,
    updateRole,
    deleteRole,
    getUsersByRole,
    getAllUser,
    getRoleMenus,
    getAllMenus,
    setRoleMenus,
    addUser,
    deleteUser
  };
};
