from django.urls import path
from drawlogic import views

urlpatterns = [
  path('', views.index, name='index'),
  path('draw/', views.draw, name='draw')
]
