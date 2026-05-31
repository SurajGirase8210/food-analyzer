# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('about/', views.about, name='about'),
#     path('analyze/', views.analyze, name='analyze'),
    
    
    
#      # AUTH (IMPORTANT)
#     path('signup/', views.signup_view, name='signup'),
#     path('login/', views.login_view, name='login'),
#     path('logout/', views.logout_view, name='logout'),

#     # API
#     path('analyze/do/', views.predict, name='analyze_api'),
    
    
# ]
print("analyzer_app urls loaded")

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('analyze/', views.analyze_page, name='analyze'),
    path('predict/', views.predict, name='predict'),
    path('about/', views.about, name='about'),

    # API
    path('analyze/do/', views.analyze_image, name='analyze_image'),

    # AUTH ROUTES (MUST BE HERE)
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('history/', views.history_view, name='history'),
    path('profile/', views.profile_view, name='profile'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # forgot password
    path(
    'password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='password_reset.html'
    ),
    name='password_reset'
),

path(
    'password-reset/done/',
    auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ),
    name='password_reset_done'
),

path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ),
    name='password_reset_confirm'
),

path(
    'reset/done/',
    auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ),
    name='password_reset_complete'
),
]