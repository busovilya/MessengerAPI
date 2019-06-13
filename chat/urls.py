from django.urls import path

from . import views

urlpatterns = [
    path('<int:pk>/', views.ChatView.as_view({'get': 'retrieve'}),
         name='get-chat-view'),
    path('', views.ChatView.as_view({'get': 'list', 'post': 'create'}),
         name='chats-view'),
    path('<int:pk>/participants/', views.ChatParticipantsView.as_view(),
         name='chat-participants-view'),
    path('<int:pk>/messages/', views.MessageView.as_view({'get': 'list'}),
         name='chat-messages-view'),
    path('messages/<int:pk>/', views.MessageView.as_view({'get': 'retrieve', 'put': 'update'}),
         name='messages-view'),
    path('messages/', views.MessageView.as_view({'post': 'create'}),
         name='create-message-view')
]
