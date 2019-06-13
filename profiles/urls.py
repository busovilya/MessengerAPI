from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserListView.as_view({'get': 'list'}), name='users'),
    path('register/', views.RegisterUserView.as_view(), name='registration')
]
