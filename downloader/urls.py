from django.urls import path

from . import views

urlpatterns=[
    path('',views.mainapp,name='mainapp'),
    path('download',views.any_downloader,name="any_downloader"),
]