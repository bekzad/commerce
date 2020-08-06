from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .models import User, Listing, Bid, Comment, Watchlist
from .forms import CreateListing, CreateBid, CreateComment

def index(request):
    listings = Listing.objects.filter(active=True)

    # Get the bids from the database to use them for current price when there has never been any bids
    for listing in listings:
        bids = listing.bids.all()
        if bids: 
            listing.current_price = listing.bids.last().price
        else:
            listing.current_price = listing.starting_price
        listing.save()

    return render(request, "auctions/index.html", {
        "listings":listings
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
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username and/or email is already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        form = CreateListing(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_price = form.cleaned_data["starting_price"]
            category = form.cleaned_data["category"]

            if form.cleaned_data["image"]:
                image = form.cleaned_data["image"]
            else:
                image = 'https://sisterhoodofstyle.com/wp-content/uploads/2018/02/no-image-1.jpg'

            newListing = Listing(user=request.user,title=title,description=description,image=image,active=True,starting_price=starting_price,category=category)
            newListing.save()

        else:
            return render(request, "auctions/create_listing.html", {
                "form": form 
            })

        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create_listing.html", {
        "form": CreateListing()
    })

def listing(request, listing_id):
    # Try to get the listing from database by the id provided
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing does not exist") 

    # Also to find out who is the last bidder
    bids = listing.bids.all()
    if bids: 
        bidder = listing.bids.last().user
    else:
        bidder = None

    # Get the comments from the database
    comments = listing.comments.all()

    # If listing is active
    if listing.active:
        # If the user is signed in render a template with watchlist
        if request.user.is_authenticated:
            # If the listing has ever been watchlisted
            try:
                watchlist = Watchlist.objects.get(user=request.user, listing=listing)

                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "watchlist":watchlist.active,
                    "bidForm": CreateBid(),
                    "bidder": bidder,
                    "create_comment":CreateComment(),
                    "comments":comments
                })
            # If the listing has never been watchlisted
            except Watchlist.DoesNotExist:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "watchlist":"never_watchlisted",
                    "bidForm": CreateBid(),
                    "bidder": bidder,
                    "create_comment":CreateComment(),
                    "comments":comments
                })
        
        # If the user isn't signed in render a template without watchlist
        return render(request, "auctions/listing.html", {
                "listing": listing,
                "bidder": bidder,
                "comments":comments
            })

    # If listing is not active show who won the auction
    else:
        if request.user == listing.winner or request.user == listing.user:
            return render(request, "auctions/winner.html", {
                "listing": listing
            })
        else:
            raise Http404("Listing is not active")

@login_required
def watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.method == 'POST':
        form = request.POST
        try:
            watchlist = Watchlist.objects.get(user=request.user, listing=listing)
            if form["watchlist"] == "watchlist":
                watchlist.active = True
                watchlist.save()
            else:
                watchlist.active = False
                watchlist.save()
        except ObjectDoesNotExist:
            watchlist = Watchlist(user=request.user, listing=listing, active=True)
            watchlist.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    if request.method == 'POST':

        bids = listing.bids.all()
        if bids: 
            current_price = listing.bids.last().price
        else:
            current_price = listing.starting_price
        
        userBid = CreateBid(request.POST)
        if userBid.is_valid():
            if len(bids) == 0:
                if userBid.cleaned_data['price'] < current_price:
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
                else:
                    newBid = Bid(price=userBid.cleaned_data['price'],listing=listing,user=request.user) 
                    listing.current_price = current_price
                    newBid.save()
                    listing.save()
            else:
                if userBid.cleaned_data['price'] <= current_price:
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
                else:
                    newBid = Bid(price=userBid.cleaned_data['price'],listing=listing,user=request.user) 
                    listing.current_price = current_price
                    newBid.save()
                    listing.save()

        bids = listing.bids.all()
        listing.number_of_bids = len(bids)
        listing.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def close_listing(request, listing_id):
    if request.method == 'POST':

        listing = Listing.objects.get(pk=listing_id)
        listing.active = False

        try:
            bidder = listing.bids.last().user
        except AttributeError:
            bidder = None

        listing.winner = bidder
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def comment(request, listing_id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        user_comment = CreateComment(request.POST)
        if user_comment.is_valid():
            newComment = Comment(text_comment=user_comment.cleaned_data['text_comment'], user=request.user, listing=listing)
            newComment.save()
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def watchlist_page(request):

    watchlists = request.user.my_watchlist.filter(active=True)

    listings = []
    for watchlist in watchlists:
        listings.append(watchlist.listing)

    return render(request, "auctions/watchlist.html",{
        "listings":listings
    })

def category_page(request):

    categories = [
    ("COL", 'Collectibles'),
    ("BOK", 'Books'),
    ("ELE", 'Electronics'),
    ("FAS", 'Fashion'),
    ("HOM", 'Home and Garden'),
    ("AUT", 'Auto parts'),
    ("MUS", 'Musical instruments'),
    ("SPO", 'Sporting goods'),
    ("TOY", 'Toys and Hobbies'),
    ("OTH", 'Other'),
    ]

    return render(request, "auctions/categories.html", {
        "categories":categories
    })

def category(request, category_name):

    listings = Listing.objects.filter(category=category_name, active=True)

    return render(request, "auctions/category.html", {
        "listings":listings
    })