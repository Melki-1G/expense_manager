from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Créer un routeur pour les ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'expenses', views.ExpenseViewSet, basename='expense')
router.register(r'bills', views.BillViewSet, basename='bill')
router.register(r'profile', views.UserProfileViewSet, basename='userprofile')

urlpatterns = [
    # URLs pour l'authentification
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    
    # URLs pour les ViewSets
    path('api/', include(router.urls)),
]

