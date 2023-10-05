from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create_listing, name="create_listing"),
    path("listing/<str:id>", views.view_listing, name="view_listing"),
    path("addwatchlist/<str:id>", views.add_watchlist, name="add_watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("comment/<str:id>", views.comment, name="comment"),
    path("removewatchlist/<str:id>", views.remove_watchlist, name="remove_watchlist"),
    path("makebid/<str:id>", views.make_bid, name="make_bid"),
    path("closebid/<str:id>", views.close_bid, name="close_bid"),
    path("openbid/<str:id>", views.open_bid, name="open_bid"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:cat>", views.view_category, name="view_category")
]