# -- coding: utf-8 --
# @File: base_utils.py
# @Time: 2025/3/10 18:29
# @Author: windyzhao
import time


# from plugins.base import CloudPlatform


def set_dir_size(dir_object, object_lists, cloud_type="aliyun"):
    next_objects = [item for item in object_lists if item.parent == dir_object.name]
    file_objects_sum = sum([item.size for item in next_objects if item.type == "FILE"])
    dir_objects_list = [item for item in next_objects if item.type == "DIR"]
    if dir_objects_list:
        for item in dir_objects_list:
            set_dir_size(item, object_lists)
    size = sum([item.size for item in dir_objects_list]) + file_objects_sum
    dir_object.size = round(size / 1024 / 1024, 2)
    if cloud_type == "fusioncloud":
        dir_object["dir_size"] = round(size / 1024 / 1024, 2)


# def get_format_method(cloud_type, resource, **kwargs):
#     """
#     获取格式化方法
#     Args:
#         cloud_type (str): 云平台类型 取值参照云平台枚举 Aliyun
#         resource (str): 资源类型名 region
#         **kwargs (): 需要添加的额外参数 如region_id等（这里不要传cloud_type）
#
#     Returns:
#         function obj
#     """
#     instance = _get_format_instance(cloud_type, **kwargs)
#     method_name = "format_{}".format(resource)
#     if not hasattr(instance, method_name):
#         raise AttributeError("方法{}不存在于{}的格式化类中".format(method_name, cloud_type))
#     return getattr(instance, method_name)


# def _get_format_instance(cloud_type, **kwargs):
#     """
#     获取格式化资源数据的实例
#     :param kwargs:  公共数据 如region、zone等，多个资源都需要。这里保留位置备用
#     :type kwargs:
#     :return:
#     :rtype:
#     """
#     if not cloud_type:
#         raise Exception("cloud_type参数不能为空")
#     kwargs["cloud_type"] = cloud_type
#     return FormatResourceFactory().create_cloud_format_obj(**kwargs)


# class FormatResourceFactory:
#     """根据云平台创建对应云平台格式化类实例"""
#
#     _instance_lock = threading.Lock()
#
#     def __init__(self):
#         self.cloud_dict = {
#             CloudPlatform.Aliyun: "_create_aliyun_instance",
#             CloudPlatform.Apsara: "_create_aliyun_instance",  # 结构与阿里云一致
#             CloudPlatform.QCloud: "_create_qcloud_instance",
#             CloudPlatform.HuaweiCloud: "_create_huaweicloud_instance",
#             CloudPlatform.VMware: "_create_vmware_instance",
#             CloudPlatform.OpenStack: "_create_openstack_instance",
#             CloudPlatform.TCE: "_create_tce_instance",
#             CloudPlatform.FusionCloud: "_create_fusioncloud_instance",
#             CloudPlatform.TKE_CLOUD: "_create_tkecloud_instance",
#             CloudPlatform.TDSQL: "_create_tdsql_instance",
#             CloudPlatform.EasyStack: "_create_easystack_instance",
#             CloudPlatform.Cas: "_create_cas_instance",
#             CloudPlatform.TSF: "_create_tsf_instance",
#             CloudPlatform.QingCloud: "_create_qingcloud_instance",
#             CloudPlatform.AmazonAws: "_create_amazonaws_instance",
#             CloudPlatform.QingCloudPrivate: "_create_qingcloud_instance",
#         }
#
#     def __new__(cls, *args, **kwargs):
#         """
#         支持多线程的单例模式
#         :param args:
#         :type args:
#         :param kwargs:
#         :type kwargs:
#         """
#         if not hasattr(FormatResourceFactory, "_instance"):
#             with FormatResourceFactory._instance_lock:
#                 if not hasattr(FormatResourceFactory, "_instance"):
#                     FormatResourceFactory._instance = object.__new__(cls)
#         return FormatResourceFactory._instance
#
#     # @staticmethod
#     # def _create_amazonaws_instance(**kwargs):
#     #     return AmazonAwsFormatResource(**kwargs)
#     #
#     # @staticmethod
#     # def _create_qingcloud_instance(**kwargs):
#     #     return QingCloudFormatResource(**kwargs)
#     #
#     # @staticmethod
#     # def _create_tsf_instance(**kwargs):
#     #     return TSFResourceFormat(**kwargs)
#     #
#     @staticmethod
#     def _create_aliyun_instance(**kwargs):
#         return None
#         # return AliyunResourceFormat(**kwargs)
#
#     #
#     # @staticmethod
#     # def _create_qcloud_instance(**kwargs):
#     #     return QCloudResourceFormat(**kwargs)
#     #
#     # @staticmethod
#     # def _create_huaweicloud_instance(**kwargs):
#     #     return HuaweicloudFormatResource(**kwargs)
#     #
#     # @staticmethod
#     # def _create_openstack_instance(**kwargs):
#     #     return OpenStackFormatResource(**kwargs)
#     #
#     # @staticmethod
#     # def _create_tce_instance(**kwargs):
#     #     return TCEResourceFormat(**kwargs)
#     #
#     # @staticmethod
#     # def _create_fusioncloud_instance(**kwargs):
#     #     return FusionCloudFormatResource(**kwargs)
#     #
#     # @staticmethod
#     # def _create_tkecloud_instance(**kwargs):
#     #     return TKECloudResourceFormat(**kwargs)
#     #
#     # @staticmethod
#     # def _create_easystack_instance(**kwargs):
#     #     return EasyStackFormatResource(**kwargs)
#     #
#     # @staticmethod
#     # def _create_cas_instance(**kwargs):
#     #     return CasFormatResource(**kwargs)
#     #
#     # @staticmethod
#     # def _create_vmware_instance(**kwargs):
#     #     return VmWareResourceFormat(**kwargs)
#     #
#     # @staticmethod
#     # def _create_tdsql_instance(**kwargs):
#     #     return TDSQLResourceFormat(**kwargs)
#
#     def create_cloud_format_obj(self, **kwargs):
#         cloud_type = kwargs["cloud_type"]
#         if cloud_type not in self.cloud_dict:
#             raise Exception("传入参数{}有误，无法找到对应云平台。请参照云平台枚举取值".format(cloud_type))
#         return getattr(self, self.cloud_dict[cloud_type])(**kwargs)


def convert_to_prometheus_format(data):
    """
    将采集信息转换为Prometheus兼容的文本格式

    输出格式示例：
    # HELP vmware_vc_info Auto-generated help for vmware_vc_info
    # TYPE vmware_vc_info gauge
    vmware_vc_info{inst_name="VMware vCenter Server",vc_version="7.0.3"} 1 1742267662301
    # HELP vmware_ds_info Auto-generated help for vmware_ds_info
    # TYPE vmware_ds_info gauge
    vmware_ds_info{inst_name="datastore1-16.16",resource_id="datastore-1646",storage="2505",system_type="VMFS",
    url="ds:///vmfs/volumes/6385b001-37c96502-d73f-509a4c67b4c3/",vmware_esxi="host-1645"} 1 1742267662301
    ...
    注意：时间戳为13位毫秒级，最后以换行符结尾
    """
    # 生成毫秒级时间戳
    timestamp = int(time.time() * 1000)

    def escape_value(value):
        """转义Prometheus标签值中的特殊字符，同时将非字符串转换为字符串"""
        if isinstance(value, str):
            return value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return str(value)

    # 用于存放所有指标，结构为{metric_name: [line, line, ...]}
    metrics = {}

    # 遍历每个模型，例如：vmware_vc、vmware_ds、vmware_vm、vmware_esxi
    for model_id, items in data.items():
        for item in items:
            # 构造标签字典：过滤掉列表和字典类型，并且值不为None
            labels = {
                k: escape_value(v)
                for k, v in item.items()
                if not isinstance(v, (list, dict)) and v is not None
            }
            labels['model_id'] = model_id
            # 按键排序生成标签字符串
            label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
            # 生成info指标，值固定为1，包含所有维度
            info_metric = f"{model_id}_info"
            info_line = f'{info_metric}{{{label_str}}} 1 {timestamp}'
            metrics.setdefault(info_metric, []).append(info_line)

    # 生成输出文本：每个指标输出一次 HELP 和 TYPE 信息，然后输出所有指标行
    output_lines = []
    for metric_name, lines in metrics.items():
        output_lines.append(f"# HELP {metric_name} Auto-generated help for {metric_name}")
        output_lines.append(f"# TYPE {metric_name} gauge")
        output_lines.extend(lines)
    # 确保最后以换行符结尾
    return "\n".join(output_lines) + "\n"
