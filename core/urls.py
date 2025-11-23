"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('employee/', include('Employee.urls')),
    path('company/', include('Company.urls')),
    path('projects/', include('projects.urls')),
    path('emaildomains/', include('EmailDomain.urls')),
    path('userroles/', include('Users.urls')),
    path('materialtype/', include('MaterialType.urls')),
    path('supergroup/', include('supergroups.urls')),
    path('matgroups/', include('matgroups.urls')),
    
    path('matgattribute/', include('matg_attributes.urls')),
    path('itemmaster/', include('itemmaster.urls')),
    path('requests/', include('requests.urls')),
    path('signup_requests/', include('signup_requests.urls')),
    path('approvals/', include('Approvals.urls')),
    path('signup_requests/', include('signup_requests.urls')),
    path('approvals/', include('Approvals.urls')),
    path('permissions/', include('permissions.urls')),
    path('validationlists/', include('validationlists.urls')),
    path("api/", include("material_api.urls")),
    path('uploads/', include('uploads.urls')),
    path('favorites/', include('favorites.urls')),
]
