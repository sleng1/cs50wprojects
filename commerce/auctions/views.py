from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Comment, Bid

def index(request):
    return render(request, "auctions/index.html", {
       "listings": Listing.objects.all()
       })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def create_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        if any([not request.POST["name"], not request.POST["description"],
               not request.POST["starting_bid"]]):
            return render(request, "auctions/createlisting.html", {
                "error": "Must fill out all required fields!!"
            })
        Listing.objects.create(
            name=request.POST["name"], 
            description=request.POST["description"], 
            starting_bid=request.POST["starting_bid"],
            image=request.POST["picture"],
            category=request.POST["category"],
            listing_user=request.user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/createlisting.html")

def view_listing(request, id):
    listing = Listing.objects.get(id=id)
    if Bid.objects.filter(item=id).order_by("-price"):
        winning_bid = Bid.objects.filter(item=id).order_by("-price")[0]
    else:
        winning_bid = listing.starting_bid
    if listing.is_closed == True:
        return render(request, "auctions/closed_listing.html", {
            "listing": listing,
            "winning_bid": winning_bid
        })
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": listing.listing_comments.all(),
        "bids": listing.listing_bids.all()
    })

def add_watchlist(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    listing = Listing.objects.get(id=id)
    if listing.is_closed == True:
        return HttpResponseRedirect(reverse("view_listing", args=[listing.id]))
    if listing.listing_user == request.user:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "message": "Cannot add your own item to watchlist!",
            "comments": listing.listing_comments.all(),
            "bids": listing.listing_bids.all()
        })
    if request.user in listing.listing_watchlist.all():
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "message": "Item already on watchlist.",
            "comments": listing.listing_comments.all(),
            "bids": listing.listing_bids.all()
        })
    listing.listing_watchlist.add(request.user)
    return HttpResponseRedirect(reverse("watchlist"))

def remove_watchlist(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    listing = Listing.objects.get(id=id)
    if listing.is_closed == True:
        return HttpResponseRedirect(reverse("view_listing", args=[listing.id]))
    if request.user in listing.listing_watchlist.all():
        listing.listing_watchlist.remove(request.user)
        return HttpResponseRedirect(reverse("watchlist"))

def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request, "auctions/watchlist.html", {
        "on_watchlist": request.user.user_watchlist.all()
    })

def comment(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        commenter = request.user
        listing = Listing.objects.get(id=id)
        comment = request.POST["comment"]
        if listing.is_closed == True:
            return HttpResponseRedirect(reverse("view_listing", 
                                                args=[listing.id]))
        if comment == "":
            return HttpResponseRedirect(reverse("view_listing", 
                                                args=[listing.id]))
        Comment.objects.create(
            commenter=commenter,
            listing=listing,
            comment=comment
        )
        return HttpResponseRedirect(reverse("view_listing", args=[listing.id]))
    
def make_bid(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        user = request.user
        item = Listing.objects.get(id=id)
        price = request.POST["bid"]
        if item.is_closed == True:
            return HttpResponseRedirect(reverse("view_listing", args=[item.id]))
        if item.listing_user == request.user:
            return render(request, "auctions/listing.html", {
                "listing": item,
                "message": "Cannot bid on your own item!",
                "comments": item.listing_comments.all(),
                "bids": item.listing_bids.all()
            })
        if not price or float(price) < item.starting_bid:
            return render(request, "auctions/listing.html", {
                "listing": item,
                "message": "Bid must be larger than starting price!",
                "comments": item.listing_comments.all(),
                "bids": item.listing_bids.all()
            })
        if item.listing_bids.all() and float(price) <= \
        max([bid.price for bid in item.listing_bids.all()]):
            return render(request, "auctions/listing.html", {
                "listing": item,
                "message": "Bid must be larger than all preceding bids!",
                "comments": item.listing_comments.all(),
                "bids": item.listing_bids.all()
            })
        Bid.objects.create(
            user=user,
            item=item,
            price=price
        )
        return HttpResponseRedirect(reverse("view_listing", args=[item.id]))

def close_bid(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login")) 
    listing = Listing.objects.get(id=id)
    if listing.listing_user != request.user:
        return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "Cannot close a listing that isn't yours!",
                "comments": listing.listing_comments.all(),
                "bids": listing.listing_bids.all()
        })
    listing.is_closed = True
    listing.save()
    return HttpResponseRedirect(reverse("view_listing", args=[listing.id]))

def open_bid(request, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login")) 
    listing = Listing.objects.get(id=id)
    if listing.listing_user != request.user:
        return render(request, "auctions/listing.html", {
                "listing": listing,
                "message": "Cannot close a listing that isn't yours!",
                "comments": listing.listing_comments.all(),
                "bids": listing.listing_bids.all()
        })
    listing.is_closed = False
    listing.save()
    return HttpResponseRedirect(reverse("view_listing", args=[listing.id]))

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": [l[0].capitalize() for l in
                       Listing.objects.values_list("category").distinct()
    ]})

def view_category(request, cat):
    return render(request, "auctions/viewcategories.html", {
        "listings": Listing.objects.filter(category=cat.lower())
    })