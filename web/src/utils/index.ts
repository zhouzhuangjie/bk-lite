import { Group } from '@/types/index'
/**
 * 将树形结构的数组平铺为一维数组
 * @param treeData 树形结构数据
 * @returns 平铺的一维数组
 */
export const convertTreeDataToGroupOptions = (treeData: Group[]): Group[] => {
  const flatData: Group[] = [];

  const flatten = (list: Group[]) => {
    list.forEach(item => {
      flatData.push(item);
      if (item.children) {
        flatten(item.children);
      }
    });
  };
  flatten(treeData);
  return flatData;
};
