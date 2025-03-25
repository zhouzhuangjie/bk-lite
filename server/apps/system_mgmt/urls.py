from rest_framework import routers

from apps.system_mgmt.viewset import ChannelViewSet, GroupViewSet, RoleViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r"group", GroupViewSet, basename="group_mgmt")
router.register(r"user", UserViewSet, basename="user_mgmt")
router.register(r"role", RoleViewSet, basename="role_mgmt")
router.register(r"channel", ChannelViewSet)
urlpatterns = router.urls
