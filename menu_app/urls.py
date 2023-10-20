from django.urls import path
from . import views

app_name = "menu_app"
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:item_id>/', views.show_current, name='show_current'),
    path('menu/<str:menu_name>/', views.show_menu, name='show_menu'),
]