from django.urls import path

from .views import (
    Index, 
    ListingDetailView, 
    ListingCreateView,
    ListingUpdateView,
    ListingDeleteView,
)
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("categories/", views.category, name="category"),
    path("categories/<int:id>/", views.category_listings, name="category-listings"),
    path("watchlist/<int:pk>/", views.watchlist, name="watchlist"),
    path("winnings/<int:pk>/", views.winnings, name="winnings"),
    path("listing/user/<int:pk>/", views.userListings, name="listing-user"),
    path("listing/new/", ListingCreateView.as_view(), name="listing-create"),
    path("listing/<int:pk>/", views.listing_detail, name="listing-detail"),
    path("listing/<int:pk>/update/", ListingUpdateView.as_view(), name="listing-update"),
    path("listing/<int:pk>/delete/", ListingDeleteView.as_view(), name="listing-delete"),
]   
