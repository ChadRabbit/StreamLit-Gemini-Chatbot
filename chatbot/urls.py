from django.urls import path
from . import views
urlpatterns=[
    path('chats',views.chatbot,name='chatbot'),
    path('login',views.login,name='login'),
    path('register',views.register,name='register'),
    path('logout',views.logout,name='logout')
]
