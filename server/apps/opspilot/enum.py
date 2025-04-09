from django.db import models
from django.utils.translation import gettext_lazy as _


class ChannelChoices(models.TextChoices):
    ENTERPRISE_WECHAT = ("enterprise_wechat", _("Enterprise WeChat"))
    ENTERPRISE_WECHAT_BOT = ("enterprise_wechat_bot", _("Enterprise WeChat Bot"))
    WECHAT_OFFICIAL_ACCOUNT = ("wechat_official_account", _("WeChat Official Account"))
    DING_TALK = ("ding_talk", _("Ding Talk"))
    WEB = ("web", _("Web"))
    GITLAB = ("gitlab", _("GitLab"))
