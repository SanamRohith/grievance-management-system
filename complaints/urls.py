from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path('about/', views.about, name='about'),
    path('login/', views.custom_login, name='login'),
    path('register/', views.register, name='register'),
    path('student_login/', views.student_login, name='student_login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('lodge_complaint/',views.lodge_complaint,name='lodge_complaint'),
    path('complaint_history/', views.complaint_history, name='complaint_history'),
    path('profile/',views.profile,name='profile'),
    path('password_reseted/',views.password_reset,name='password_reseted'),
    path('logout/',views.logout,name='logout'),
    path('admin/logout/', auth_views.LogoutView.as_view(), {'next_page': '/admin/login/'}, name='admin_logout'),

    path('password_reset_form/', auth_views.PasswordResetView.as_view(template_name='complaints/password_reset_form.html'),name='password_reset_form'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='complaints/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='complaints/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(template_name='complaints/password_reset_complete.html'), name='password_reset_complete'),
] 


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



    
