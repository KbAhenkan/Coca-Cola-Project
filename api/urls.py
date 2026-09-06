from django.urls import path
from . import views

urlpatterns = [
    # AUTH URLS
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),

    # USER URLS
    path('place_order/', views.place_order, name='place order'),
    path('view_order/', views.view_order, name='view order'),
    path('browse/', views.browse, name='browse'),

    # PRODUCT URLS
    path('product/', views.product_list, name='product list'),
    path('product/<int:pk>/', views.product_details, name='product detail'),
]
