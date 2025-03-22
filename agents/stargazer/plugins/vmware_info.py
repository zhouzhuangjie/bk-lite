# -- coding: utf-8 --
# @File: vmware_info.py
# @Time: 2025/2/26 11:08
# @Author: windyzhao

import time

from pyVim.connect import ConnectNoSSL, Disconnect, SmartConnect
from pyVmomi import vim
from sanic.log import logger



class VmwareManage(object):
    def __init__(self, params: dict):
        self.params = params
        self.password = params.get("password")
        self.user = params.get("username")
        self.host = params.get("hostname")
        self.port = params.get("port", 443)
        self.ssl = params.get("ssl", "false") == "true"
        self.si = self.connect_vc()
        self.content = self.si.RetrieveContent()

    def test_connection(self):
        """
        Test connection to vcenter
        :return:
        """
        try:
            self.si = self.connect_vc()
            self.content = self.si.RetrieveContent()
            return True
        except Exception as err:
            logger.error(f"test_connection error! {err}")
            return False

    def get_all_objs(self, obj_type, folder=None):
        if folder is None:
            container = self.content.viewManager.CreateContainerView(self.content.rootFolder, obj_type, True)
        else:
            container = self.content.viewManager.CreateContainerView(folder, obj_type, True)
        return container.view

    def connect_vc(self):
        try:
            params = dict(host=self.host, port=int(self.port), user=self.user, pwd=self.password)
            si = SmartConnect(**params) if self.ssl else ConnectNoSSL(**params)
            return si
        except Exception as err:
            logger.error(f"connect vcenter error! {err}")
            return

    def get_hosts(self):
        result = []
        cluster_list = self.get_all_objs(obj_type=[vim.ComputeResource])
        for cluster in cluster_list:
            for host in cluster.host:
                ip_addr = ""
                try:
                    if host.config and host.config.network:
                        if host.config.network.vnic:
                            for nic in host.config.network.vnic:
                                ip_addr = nic.spec.ip.ipAddress
                                break
                    else:
                        if host.summary and host.summary.managementServerIp:
                            ip_addr = host.summary.managementServerIp
                        else:
                            logger.warning("Host config or network is None and no managementServerIp found")
                except Exception as err:
                    logger.error(f"get_hosts host ip_add error! {err}")

                esxi_version = ""
                try:
                    esxi_version = host.config.product.version
                except Exception as err:
                    logger.error(f"get_hosts host.config.product.version host esxi_version error! {err}")

                if not esxi_version:
                    try:
                        esxi_version = host.summary.config.product.version
                    except Exception as err:
                        logger.error(f"get_hosts host.summary.config.product host esxi_version error! {err}")

                memory_total = host.hardware.memorySize // 1024 // 1024

                result.append(
                    {
                        "ip_addr": ip_addr,
                        # "inst_name": host.name,
                        "inst_name": f"{host.name}[{host._moId}]",
                        "resource_id": host._moId,
                        "memory": memory_total,
                        "cpu_model": host.summary.hardware.cpuModel,
                        "cpu_cores": host.summary.hardware.numCpuCores,
                        "vcpus": host.summary.hardware.numCpuThreads,
                        "esxi_version": esxi_version,
                        "vmware_ds": ",".join(i._moId for i in host.datastore),

                    }
                )

        return result

    @staticmethod
    def _get_vm_prop(vm, attributes):
        result = vm
        for attribute in attributes:
            try:
                result = getattr(result, attribute)
            except (AttributeError, IndexError):
                return None
        return result

    def get_vms(self):
        result = []
        try:
            vm_list = self.get_all_objs(obj_type=[vim.VirtualMachine])
            for vm in vm_list:
                if vm.config and vm.config.template:
                    continue

                vm_dict = {
                    "resource_id": vm._moId,
                    "inst_name": f"{vm.name}[{vm._moId}]",
                    "ip_addr": "",
                    "vmware_esxi": "",
                    "vmware_ds": "",
                    "cluster": "",
                    "os_name": "",
                    "vcpus": "",
                    "memory": "",
                }

                vmnet = self._get_vm_prop(vm, ("guest", "net"))
                if vmnet:
                    net_dict = {}
                    for device in vmnet:
                        net_dict[device.macAddress] = dict()
                        net_dict[device.macAddress]["ipv4"] = []
                        net_dict[device.macAddress]["ipv6"] = []
                        for ip_addr in device.ipAddress:
                            if "::" in ip_addr:
                                net_dict[device.macAddress]["ipv6"].append(ip_addr)
                            else:
                                net_dict[device.macAddress]["ipv4"].append(ip_addr)

                    for _vmnet in net_dict.values():
                        if _vmnet["ipv4"]:
                            vm_dict["ip_addr"] = _vmnet["ipv4"][0]
                            break

                    if not vm_dict["ip_addr"]:
                        for _vmnet in net_dict.values():
                            if _vmnet["ipv6"]:
                                vm_dict["ip_addr"] = _vmnet["ipv6"][0]
                                break

                if vm.summary.runtime.host:
                    vm_dict["vmware_esxi"] = vm.summary.runtime.host._moId
                    if isinstance(vm.summary.runtime.host.parent, vim.ClusterComputeResource):
                        vm_dict["cluster"] = vm.summary.runtime.host.parent.name

                vm_dict["vmware_ds"] = ",".join(datastore._moId for datastore in vm.datastore)
                vm_dict["vcpus"] = vm.summary.config.numCpu
                vm_dict["os_name"] = vm.summary.config.guestFullName
                vm_dict["memory"] = vm.summary.config.memorySizeMB

                result.append(vm_dict)

        except Exception as err:
            logger.error(f"get_vms error! {err}")

        return result

    def get_datastore(self):
        result = []
        cluster_list = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.ComputeResource], True
        ).view
        for cluster in cluster_list:
            result.append({"name": cluster.name, "moid": cluster._moId})
        return result

    def get_datacenters_and_datastore(self):
        datastore_list = []
        datacenters_list = []
        try:
            container = self.get_all_objs(obj_type=[vim.Datacenter])
            for datacenter in container:
                datacenter_dict = {
                    "moid": datacenter._moId,
                    "name": datacenter.name,
                    "vc": {"name": self.content.about.name, "version": self.content.about.version},
                }
                for datastore in datacenter.datastore:
                    datastore_list.append(
                        {
                            "resource_id": datastore._moId,
                            "url": datastore.summary.url,
                            # "inst_name": datastore.summary.name,
                            "inst_name": f"{datastore.summary.name}[{datastore._moId}]",
                            "system_type": datastore.summary.type,
                            "storage": datastore.summary.capacity // 1024 // 1024 // 1024,
                            "vmware_esxi": ",".join(host.key._moId for host in datastore.summary.datastore.host),
                        }
                    )
                datacenters_list.append(datacenter_dict)
        except Exception as err:
            logger.error(f"get_datacenters_and_datastore error! {err}")

        return datacenters_list, datastore_list

    def service(self):
        vc_name = self.content.about.name
        vc_version = self.content.about.version
        datacenters, datastore = self.get_datacenters_and_datastore()
        vm_list = self.get_vms()
        esxi = self.get_hosts()

        result = {
            "vmware_vc": [{"vc_version": vc_version, "inst_name": vc_name}],
            "vmware_ds": datastore,
            "vmware_vm": vm_list,
            "vmware_esxi": esxi,
        }

        return result

    def disconnect_vc(self):
        Disconnect(self.si)

    def list_all_resources(self):
        try:
            result = self.service()
        except Exception as err:
            logger.error(f"vmware_info main error! {err}")
            result = []

        try:
            self.disconnect_vc()
        except:
            pass

        lines = self.convert_to_prometheus_format(result)
        return lines

    @staticmethod
    def convert_to_prometheus_format(data):
        """
        将VMware信息转换为Prometheus兼容的文本格式

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
