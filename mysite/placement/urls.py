from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='home'),
    path('analyze/', views.student_form, name='analyze'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/', views.export_csv, name='export'),
    path('export-csv/', views.export_students_csv, name='export_csv'),
    path('profile/', views.profile, name='profile'),
    path('support/', views.support, name='support'),
]