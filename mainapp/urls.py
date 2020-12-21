from django.urls import path, include
from . import views
from .views import ProductDetailView, CartView
urlpatterns = [
    path('', views.index, name='home'),
    path('smartphone', views.smartPhone, name='smartphone'),
    path('notebook', views.noteBook, name='notebook'),
    path('detail_smartphone', views.detail_smartphone, name='detail_smartphone'),
    path('detail_smartphone', views.detail_notebook, name='detail_notebook'),
    path('notebook/<int:id>/<slug:slug>/', views.product_detail_n, name='product_detail'),
    path('smartphone/<int:id>/<slug:slug>/', views.product_detail_s, name='product_detail'),
    path('cart/',CartView.as_view(), name='cart')
]

