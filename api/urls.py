from django.urls import path
from . import views

urlpatterns = [
    # AUTH URLS
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),

    # USER(ORDER) URLS
    path('place_order/', views.place_order, name='place order'),
    path('view_order/', views.view_order, name='view order'),
    path('modify_order/<int:pk>/', views.modify_order, name='modify order'),
    path('browse/', views.browse, name='browse'),

    # CATEGORY URLS
    path('category_browse/', views.category_browse, name='browse category'),
    path('category/', views.category_list, name='category list'),
    path('category/<int:pk>/', views.category_details, name='category detail'),


    # PRODUCT URLS
    path('product/', views.product_list, name='product list'),
    path('product/<int:pk>/', views.product_details, name='product detail'),

    # REVIEW URLS
    path('review/', views.create_review, name='create review'),
    path('view_review/', views.view_review, name= 'view review'),

    # COUPON URLS
    path('coupon_browse/', views.coupon_browse, name='browse coupon'),
    path('coupon/', views.coupon_list, name='coupon list'),
    path('coupon/<int:pk>/', views.coupon_details, name='coupon detail'),
    
]
