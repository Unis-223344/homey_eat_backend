from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DishViewSet, CategoryViewSet, SubcategoryViewSet


router = DefaultRouter()
router.register(r'dishes', DishViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubcategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
