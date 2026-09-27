from django.urls import path
from . import views

urlpatterns = [

    # Home
    path('', views.home, name='home'),

    # Farmer
    path('register_farmer/', views.register_farmer, name='register_farmer'),
    path('farmer_login/', views.farmer_login, name='farmer_login'),
    path('farmer_dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('add_crop/', views.add_crop, name='add_crop'),
    path('edit_crop/<int:crop_id>/', views.edit_crop, name='edit_crop'),
    path('delete_crop/<int:crop_id>/', views.delete_crop, name='delete_crop'),
    path('farmer_orders/', views.farmer_orders, name='farmer_orders'),

    # Buyer
    path('register_buyer/', views.register_buyer, name='register_buyer'),
    path('buyer_login/', views.buyer_login, name='buyer_login'),
    path('buyer_dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer_orders/', views.buyer_orders, name='buyer_orders'),

    # Marketplace
    path('marketplace/', views.marketplace, name='marketplace'),

    # Cart
    path('add_to_cart/<int:crop_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('increase/<int:crop_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:crop_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove/<int:crop_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Order + Payment
    path('place_order/', views.place_order, name='place_order'),
    path('payment/', views.payment, name='payment'),
    path('buy_now/<int:crop_id>/', views.buy_now, name='buy_now'),
    path('payment_success/', views.payment_success, name='payment_success'),

    # Order Status
    path('approve_order/<int:order_id>/', views.approve_order, name='approve_order'),
    path('reject_order/<int:order_id>/', views.reject_order, name='reject_order'),
    path('deliver_order/<int:order_id>/', views.deliver_order, name='deliver_order'),
    path(
    'price_discovery/',
    views.price_discovery,
    name='price_discovery'
),
path(
    'price_trends/',
    views.price_trends,
    name='price_trends'
),
path(
    'demand_supply/',
    views.demand_supply,
    name='demand_supply'
),
path(
    'price_alerts/',
    views.price_alerts,
    name='price_alerts'
),
path(
    'create_price_alert/',
    views.create_price_alert,
    name='create_price_alert'
),
path(
    'price_prediction/',
    views.price_prediction,
    name='price_prediction'
),
path(
    'voice_assistant/',
    views.voice_assistant,
    name='voice_assistant'
),

path(
    'voice_price_query/',
    views.voice_price_query,
    name='voice_price_query'
),
path('voice_sell/', views.voice_sell, name='voice_sell'),

path(
    'voice_sell_crop/',
    views.voice_sell_crop,
    name='voice_sell_crop'
),
]