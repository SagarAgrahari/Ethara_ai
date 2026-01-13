from rest_framework import routers
from .views import EmployeeViewSet, AttendanceViewSet

router = routers.DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'attendance', AttendanceViewSet)

urlpatterns = router.urls
