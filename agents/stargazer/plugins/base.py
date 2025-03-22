# -- coding: utf-8 --
# @File: base.py
# @Time: 2025/2/27 10:50
# @Author: windyzhao
from enum import Enum


class CloudType(Enum):
    UNKNOWNCLOUD = "unknownCloud"
    ALIYUN = "Aliyun"
    QClOUD = "QCloud"
    HUAWEICLOUD = "HuaweiCloud"
    OPENSTACK = "OpenStack"
    VMWARE = "VMware"
    FUSIONCOMPUTE = "FusionCompute"
    FUSIONCLOUD = "FusionCloud"
    MANAGEONE = "ManageOne"
    TCE = "TCE"
    TKE_CLOUD = "TKE"
    TDSQL = "TDSQL"
    APSARA = "Apsara"
    EASYSTACK = "EasyStack"
    CAS = "Cas"
    QINGCLOUD = "QingCloud"
    TSF = "TSF"
    AMAZONAWS = "AmazonAws"
    QINGCLOUDPRIVATE = "QingCloudPrivate"


RESOURCE_MAP = {
    "region": ("Regions", "Region"),
    "zone": ["Zones", "Zone"],
    "instance_type_family": ["InstanceTypeFamilies", "InstanceTypeFamily"],
    "instance_type": ["InstanceTypes", "InstanceType"],
    "vm": ["Instances", "Instance"],
    "tag": ["TagResources", "TagResource"],
    "snapshot": ["Snapshots", "Snapshot"],
    "image": ["Images", "Image"],
    "disk": ["Disks", "Disk"],
    "subnet": ["VSwitches", "VSwitch"],
    "vpc": ["Vpcs", "Vpc"],
    "eip": ["EipAddresses", "EipAddress"],
    "security_group": ["SecurityGroups", "SecurityGroup"],
    "security_group_rule": ["Permissions", "Permission"],
    "route_table": ["RouterTableList", "RouterTableListType"],
    "route_entry": ["RouteEntrys", "RouteEntry"],
    "auto_snapshot_policy": ["AutoSnapshotPolicies", "AutoSnapshotPolicy"],
    "load_balancer": ["LoadBalancers", "LoadBalancer"],
    "listener": ["Listeners", "Listener"],
    "vserver_groups": ["VServerGroups", "VServerGroup"],
    "server_certificate": ["ServerCertificates", "ServerCertificate"],
    "file_system": ["FileSystems", "FileSystem"],
    "rule": ["Rules", "Rule"],
    "domain": ["Domains", "Domain"],
}


class CloudPlatform:
    Aliyun = CloudType.ALIYUN.value
    Aliyun_cn = "阿里云"
    aliyun = "aliyun"

    Apsara = CloudType.APSARA.value
    Apsara_cn = "阿里云飞天"
    apsara = "apsara"

    QCloud = CloudType.QClOUD.value
    QCloud_cn = "腾讯云"
    qcloud = "qcloud"

    HuaweiCloud = CloudType.HUAWEICLOUD.value
    HuaweiCloud_cn = "华为云"
    huaweicloud = "huaweicloud"

    OpenStack = CloudType.OPENSTACK.value
    OpenStack_cn = "OpenStack"
    openstack = "openstack"

    VMware = CloudType.VMWARE.value
    VMware_cn = "VMware"
    vmware = "vmware"

    FusionCompute = CloudType.FUSIONCOMPUTE.value
    FusionCompute_cn = "FusionCompute"
    fusioncompute = "fusioncompute"

    FusionCloud = CloudType.FUSIONCLOUD.value
    FusionCloud_cn = "FusionCloud"
    fusioncloud = "fusioncloud"

    TKE_CLOUD = CloudType.TKE_CLOUD.value
    TKE_CLOUD_cn = "TKE"
    tke_cloud = "tke"

    unknownCloud = CloudType.UNKNOWNCLOUD.value
    unknownCloud_cn = "未知云"
    unknowncloud = "unknowncloud"

    EasyStack = CloudType.EASYSTACK.value
    EasyStack_cn = "易捷行云"
    easystack = "easystack"

    Cas = CloudType.CAS.value
    Cas_cn = "华三CAS"
    cas = "cas"

    TCE = CloudType.TCE.value
    TCE_cn = "TCE"
    tce = "tce"

    TDSQL = CloudType.TDSQL.value
    TDSQL_cn = "TDSQL"
    tdsql = "tdsql"

    QingCloud = CloudType.QINGCLOUD.value
    QingCloud_cn = "青云"
    qingcloud = "qingcloud"

    TSF = CloudType.TSF.value
    TSF_cn = "微服务平台"
    tsf = "tsf"

    AmazonAws = CloudType.AMAZONAWS.value
    AmazonAws_cn = "亚马逊云"
    amazonaws = "amazonaws"

    QingCloudPrivate = CloudType.QINGCLOUDPRIVATE.value
    QingCloudPrivate_cn = "青云私有云"
    qingcloudprivate = "qingcloudprivate"

    ALL_CLOUD = [
        QCloud,
        Aliyun,
        HuaweiCloud,
        OpenStack,
        VMware,
        FusionCompute,
        FusionCloud,
        TCE,
        TDSQL,
        Apsara,
        EasyStack,
        Cas,
        TSF,
        QingCloud,
        AmazonAws,
        QingCloudPrivate,
    ]
    ALL_CLOUD_CN = [
        QCloud_cn,
        Aliyun_cn,
        HuaweiCloud_cn,
        OpenStack_cn,
        VMware_cn,
        FusionCompute_cn,
        FusionCloud_cn,
        TCE_cn,
        TDSQL_cn,
        Apsara_cn,
        EasyStack_cn,
        Cas_cn,
        TSF_cn,
        QingCloud_cn,
        AmazonAws_cn,
        QingCloudPrivate_cn,
    ]
    CLOUD = [QCloud, Aliyun, HuaweiCloud]
    CLOUDLOWER = [qcloud, aliyun, huaweicloud]
    CLOUD_cn = ["腾讯云", "华为云", "阿里云"]
    CLOUD_CLOUD_cn = {QCloud: "腾讯云", Aliyun: "阿里云", HuaweiCloud: "华为云"}
    # 私有云
    LOCAL = [
        OpenStack,
        VMware,
        FusionCompute,
        FusionCloud,
        TCE,
        TDSQL,
        Apsara,
        EasyStack,
        Cas,
        QingCloud,
        QingCloudPrivate,
    ]
    LOCAL_cn = [
        OpenStack_cn,
        VMware_cn,
        FusionCompute_cn,
        FusionCloud_cn,
        TCE_cn,
        TDSQL_cn,
        Apsara_cn,
        EasyStack_cn,
        Cas_cn,
        QingCloud_cn,
    ]
    LOCALLOWER = [
        openstack,
        vmware,
        fusioncompute,
        fusioncloud,
        tce,
        tdsql,
        apsara,
        easystack,
        cas,
        qingcloud,
        QingCloudPrivate,
    ]
    DATABASE = [TDSQL]
    DATABASE_cn = [TDSQL_cn]
    DATABASELOWER = [tdsql]

    REGION_CLOUD = {
        QCloud,
        Aliyun,
        HuaweiCloud,
        TCE,
        OpenStack,
        FusionCloud,
        FusionCompute,
        Apsara,
        QingCloud,
        AmazonAws,
        QingCloudPrivate,
    }

    EIP_CLOUD = [QCloud, Aliyun, HuaweiCloud, TCE, FusionCloud]

    SECURITY_GROUP_CLOUD = [
        QCloud,
        Aliyun,
        HuaweiCloud,
        TCE,
        OpenStack,
        FusionCloud,
        FusionCompute,
        QingCloud,
        QingCloudPrivate,
    ]

    # 有存储资源定价 即云硬盘价格
    STORAGE_PRICE_CLOUD = [QCloud, Aliyun, HuaweiCloud, TCE]
