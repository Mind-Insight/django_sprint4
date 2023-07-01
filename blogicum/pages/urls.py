from django.urls import path

from pages import views


app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutPage.as_view(), name='about'),
    path('rules/', views.RulesPage.as_view(), name='rules'),
]
