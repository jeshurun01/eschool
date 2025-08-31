from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importer les ViewSets API quand ils seront créés
# from accounts.api import UserViewSet, StudentViewSet, TeacherViewSet
# from academic.api import ClassRoomViewSet, GradeViewSet, AttendanceViewSet
# from finance.api import InvoiceViewSet, PaymentViewSet
# from communication.api import AnnouncementViewSet, MessageViewSet

router = DefaultRouter()
# router.register(r'users', UserViewSet)
# router.register(r'students', StudentViewSet)
# router.register(r'teachers', TeacherViewSet)
# router.register(r'classes', ClassRoomViewSet)
# router.register(r'grades', GradeViewSet)
# router.register(r'attendance', AttendanceViewSet)
# router.register(r'invoices', InvoiceViewSet)
# router.register(r'payments', PaymentViewSet)
# router.register(r'announcements', AnnouncementViewSet)
# router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
