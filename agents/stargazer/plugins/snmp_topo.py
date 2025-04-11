# -- coding: utf-8 --
# @File: snmp_topo.py
# @Time: 2025/3/31 14:35
# @Author: windyzhao

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1905 import EndOfMibView

ROOT = "root"  # 根oid
KEY = "key"  # oid
TAG = "tag"  # 名称
IF_INDEX = "ifindex"  # 索引
IF_INDEX_TYPE = "ifindex_type"  # 索引类型 default为单索引,ipaddr为后4位为ip地址
VAL = "val"  # oid对应值

OIDKEY = [ROOT, KEY, TAG, IF_INDEX, IF_INDEX_TYPE, VAL]

DEFAULT_OIDS = [
    # ARP表
    {
        "key": "1.3.6.1.2.1.4.22.1.1",
        "tag": "ARP-IfIndex",
        "ifindex_type": "ipaddr",
    },
    {
        "key": "1.3.6.1.2.1.4.22.1.2",
        "tag": "ARP-PhysAddress",
        "ifindex_type": "ipaddr",
    },
    # IFTable表
    {
        "key": "1.3.6.1.2.1.2.2.1.2",
        "tag": "IFTable-IfDescr",
        "ifindex_type": "default",
    },
    {
        "key": "1.3.6.1.2.1.2.2.1.6",
        "tag": "IFTable-PhysAddress",
        "ifindex_type": "default",
    },
    # 接口别名
    {
        "key": "1.3.6.1.2.1.31.1.1.1.18",
        "tag": "IFTable-IfAlias",
        "ifindex_type": "default",
    },
    # IPARR表
    {
        "key": "1.3.6.1.2.1.4.20.1.1",
        "tag": "IpAddr-IpAddr",
        "ifindex_type": "ipaddr",
    },
]

DEFAULT_OID_MAP = {i["key"]: i for i in DEFAULT_OIDS}


def get_root_oid(oid):
    for root_oid in DEFAULT_OID_MAP.keys():
        if root_oid in oid:
            return root_oid
        else:
            return None


def build_single_oid_dict(oid, val):
    """单值OID字典"""
    root_oid = get_root_oid(oid)
    if not root_oid:
        return
    oid_dict = DEFAULT_OID_MAP.get(root_oid, {})
    return {
        ROOT: root_oid,
        KEY: oid,
        TAG: oid_dict.get("tag", "") or oid,
        IF_INDEX: None,
        IF_INDEX_TYPE: "None",
        VAL: val,
    }


def build_oid_dict(oid, val, parent_oid=None):
    """树形OID字典"""

    root_oid = get_root_oid(oid) or parent_oid or None
    if not root_oid:
        raise ValueError(f"OID {oid} not in DEFAULT_OID_MAP")

    oid_dict = DEFAULT_OID_MAP.get(root_oid, {})
    ifindex_type = oid_dict.get("ifindex_type", "default") or "default"
    if ifindex_type == "default":
        ifIndex = oid.rsplit(".", 1)[-1]
    elif ifindex_type == "ipaddr":
        ifIndex = ".".join(oid.rsplit(".", 4)[-4:])
    else:
        ifIndex = None

    return {
        ROOT: root_oid,
        KEY: oid,
        TAG: oid_dict.get("tag", "") or oid,
        IF_INDEX: ifIndex,
        IF_INDEX_TYPE: ifindex_type,
        VAL: val,
    }


class SnmpAuth(object):
    def __init__(
            self,
            cmdGen,
            version: str = "v2",
            community: str = None,
            username: str = "",
            level: str = "",
            integrity: str = None,
            privacy: str = None,
            authkey: str = None,
            privkey: str = None,
    ):
        self.cmdGen = cmdGen
        self.version = version
        self.community = community
        self.username = username
        self.level = level
        self.integrity = integrity
        self.privacy = privacy
        self.authKey = authkey
        self.privKey = privkey
        self.validate()

    def validate(self):

        if self.version in ("v2", "v2c"):
            if self.community is None:
                raise Exception("Community not set when using snmp version 2")
        if self.version == "v3":
            if self.username is None:
                raise Exception("Username not set when using snmp version 3")

        if self.level == "authPriv" and self.privacy is None:
            raise Exception("Privacy algorithm not set when using authPriv")

    def auth(self):  # Use SNMP Version 2

        if self.version in ("v2", "v2c"):
            snmp_auth = cmdgen.CommunityData(self.community)

        # Use SNMP Version 3 with authNoPriv
        else:
            integrity_proto = None
            privacy_proto = None
            if self.integrity == "sha":
                integrity_proto = cmdgen.usmHMACSHAAuthProtocol
            elif self.integrity == "md5":
                integrity_proto = cmdgen.usmHMACMD5AuthProtocol

            if self.privacy == "aes":
                privacy_proto = cmdgen.usmAesCfb128Protocol
            elif self.privacy == "des":
                privacy_proto = cmdgen.usmDESPrivProtocol

            if self.level == "authNoPriv":
                snmp_auth = cmdgen.UsmUserData(self.username, authKey=self.authKey, authProtocol=integrity_proto)

            # Use SNMP Version 3 with authPriv
            else:
                snmp_auth = cmdgen.UsmUserData(
                    self.username,
                    authKey=self.authKey,
                    privKey=self.privKey,
                    authProtocol=integrity_proto,
                    privProtocol=privacy_proto,
                )
        return snmp_auth


class SnmpTopoClient:
    def __init__(self, kwargs):
        """
        初始化 SNMP 客户端
        """
        self.kwargs = kwargs
        self.host = kwargs.get('host')
        self.version = kwargs.get('version')
        self.community = kwargs.get('community')
        self.username = kwargs.get('username')
        self.level = kwargs.get('level')
        self.integrity = kwargs.get('integrity')
        self.privacy = kwargs.get('privacy')
        self.authkey = kwargs.get('authkey')
        self.privkey = kwargs.get('privkey')
        self.timeout = int(kwargs.get('timeout', 5))
        self.retries = int(kwargs.get('retries', 1))
        self.snmp_port = int(kwargs.get('snmp_port', 161))  # 默认 SNMP 端口为 161
        self.oids = list(DEFAULT_OID_MAP.keys())
        self.cmdGen = cmdgen.CommandGenerator()
        self.auth = SnmpAuth(
            self.cmdGen, self.version, self.community, self.username, self.level, self.integrity, self.privacy,
            self.authkey, self.privkey
        ).auth()

    @staticmethod
    def _format_oids(oids):
        """
        格式化 OID 列表
        """
        return [cmdgen.MibVariable(oid.strip()) for oid in oids]

    @staticmethod
    def _format_result(varBinds, eval_oids=None):
        """
        格式化 SNMP 返回结果
        """
        result = []
        for varBindsRow in varBinds:
            for oid, val in varBindsRow:
                if isinstance(val, EndOfMibView):
                    continue
                current_oid = oid.prettyPrint()
                current_val = val.prettyPrint()
                parent_oid = (
                    next((q_oid for q_oid in eval_oids if current_oid.startswith(q_oid)), None)
                    if eval_oids
                    else None
                )
                oid_dict = build_oid_dict(current_oid, current_val, parent_oid=parent_oid)
                if oid_dict:
                    result.append(oid_dict)
        return result

    def bulkCmd(self):
        """
        批量获取 OID 数据
        """
        eval_oids = self.oids
        transport_opts = {"timeout": self.timeout, "retries": self.retries}
        oids = self._format_oids(self.oids)
        errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGen.bulkCmd(
            self.auth,
            cmdgen.UdpTransportTarget((self.host, self.snmp_port), **transport_opts),
            0,
            25,
            *oids,
            lookupMib=False,
        )
        if errorIndication:
            raise Exception(errorIndication)
        return self._format_result(varBindTable, eval_oids)

    def list_all_resources(self):
        """
        将采集到的 SNMP 数据转换为标准格式。
        """
        from plugins.base_utils import convert_to_prometheus_format
        snmp_data = self.bulkCmd()
        model_data = {"network_topo": snmp_data}
        result = convert_to_prometheus_format(model_data)
        return result

    @staticmethod
    def find_topology_links(data_source):
        """
        通用方法：根据数据源找出接口之间的关联关系。
        :param data_source: 数据源，包含SNMP采集的数据
        :return: 接口关联关系列表
        """
        data = data_source

        # 数据验证和分类
        arp_table = {}  # 存储ARP表信息：IP地址与MAC地址的映射
        if_table = {}  # 存储接口表信息：接口描述与MAC地址的映射

        for item in data:
            root = item.get("root")
            key = item.get("key")
            tag = item.get("tag")
            ifindex = item.get("ifindex")
            val = item.get("val")

            # 跳过无效数据
            if not root or not key or not tag or not ifindex or not val:
                continue

            # 分类整理数据
            if root == "1.3.6.1.2.1.4.22.1.1":  # ARP-IfIndex
                arp_table[ifindex] = {"ip": val, "ifindex": ifindex}
            elif root == "1.3.6.1.2.1.4.22.1.2":  # ARP-PhysAddress
                if ifindex in arp_table:
                    arp_table[ifindex]["mac"] = val
            elif root == "1.3.6.1.2.1.2.2.1.2":  # IFTable-IfDescr
                if_table[ifindex] = {"descr": val, "ifindex": ifindex}
            elif root == "1.3.6.1.2.1.2.2.1.6":  # IFTable-PhysAddress
                if ifindex in if_table:
                    if_table[ifindex]["mac"] = val
            elif root == "1.3.6.1.2.1.31.1.1.1.18":  # IFTable-IfAlias
                if ifindex in if_table:
                    if_table[ifindex]["alias"] = val
                else:
                    if_table[ifindex] = {"ifindex": ifindex, "alias": val}

        # 建立关联关系
        links = []
        for ifindex_arp, arp_entry in arp_table.items():
            mac = arp_entry.get("mac")
            ip = arp_entry.get("ip")

            # 跳过无效的MAC地址
            if not mac or mac == "0x000000000000":
                continue

            # 查找接口表中MAC地址匹配的项
            for ifindex_if, if_entry in if_table.items():
                if if_entry.get("mac") == mac:
                    # 构建连接关系：source为本地接口，target为远程设备
                    links.append({
                        "source": {
                            "interface": if_entry.get("descr"),
                            "alias": if_entry.get("alias", ""),  # 添加接口别名
                            "mac": if_entry.get("mac"),
                            "ifindex": ifindex_if
                        },
                        "target": {
                            "interface": "Remote Device",
                            "mac": mac,
                            "ip": ip,
                            "ifindex": arp_entry.get("ifindex")
                        },
                        "link_type": "mac_match"
                    })

        # 从数据中寻找额外的关联
        for interface in data:
            ifindex = interface.get("ifindex")
            ifindex_type = interface.get("ifindex_type")
            val = interface.get("val")

            # 跳过无效数据
            if not ifindex or not ifindex_type or not val:
                continue

            # 获取当前接口的别名
            interface_alias = ""
            if ifindex in if_table and "alias" in if_table[ifindex]:
                interface_alias = if_table[ifindex]["alias"]

            for other_interface in data:
                if other_interface == interface:
                    continue

                # 判断关联条件
                if other_interface.get("ifindex") == val and other_interface.get("ifindex_type") == ifindex_type:
                    # 获取目标接口的别名
                    target_alias = ""
                    target_ifindex = other_interface.get("ifindex")
                    if target_ifindex in if_table and "alias" in if_table[target_ifindex]:
                        target_alias = if_table[target_ifindex]["alias"]

                    links.append({
                        "source": {
                            "key": interface.get("key"),
                            "tag": interface.get("tag"),
                            "ifindex": ifindex,
                            "alias": interface_alias
                        },
                        "target": {
                            "key": other_interface.get("key"),
                            "tag": other_interface.get("tag"),
                            "ifindex": other_interface.get("ifindex"),
                            "alias": target_alias
                        },
                        "link_type": "index_match"
                    })

        return links
