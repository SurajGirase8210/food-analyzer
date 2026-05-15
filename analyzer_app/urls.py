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
]