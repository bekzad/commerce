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
            image = form.cleaned_data["image"]
            starting_price = form.cleaned_data["starting_price"]
            category = form.cleaned_data["category"]

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
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing does not exist") 

    # Get the bids from the database to use them for current price
    bids = listing.bids.all()
    if bids: 
        current_price = listing.bids.last().price
        number_of_bids = len(bids)
        bidder = listing.bids.last().user
    else:
        current_price = listing.starting_price
        number_of_bids = 0
        bidder = None

    # Get the comments from the database
    comments = listing.comments.all()

    # If listing is active
    if listing.active:
        # If the user is signed in render a template with watchlist
        if request.user.is_authenticated:
            watchlisted = listing.watchlisted.filter(user=request.user).last()
            print(watchlisted)
            watchlist = Watchlist.objects.filter(user=request.user, listing=listing).last()
            print(watchlist)
            try:
                watchlist = Watchlist.objects.get(user=request.user, listing=listing)
                
                if watchlist.active == True:
                    return render(request, "auctions/listing.html", {
                        "listing": listing,
                        "watchlist":"a",
                        "bidForm": CreateBid(),
                        "current_price": current_price,
                        "bid_number": number_of_bids,
                        "bidder": bidder,
                        "create_comment":CreateComment(),
                        "comments":comments
                    })

                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "watchlist":"n",
                    "bidForm": CreateBid(),
                    "current_price": current_price,
                    "bid_number": number_of_bids,
                    "bidder": bidder,
                    "create_comment":CreateComment(),
                    "comments":comments
                })
            except Watchlist.DoesNotExist:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "watchlist":"n",
                    "bidForm": CreateBid(),
                    "current_price": current_price,
                    "bid_number": number_of_bids,
                    "bidder": bidder,
                    "create_comment":CreateComment(),
                    "comments":comments
                })
        
        # If the user isn't signed in render a template without watchlist
        return render(request, "auctions/listing.html", {
                "listing": listing,
                "current_price": current_price,
                "bid_number": number_of_bids,
                "bidder": bidder,
                "comments":comments
            })

    # If listing is not active show who won the auction
    else:
        if request.user == listing.winner or request.user == listing.user:
            return render(request, "auctions/winner.html", {
                "listing": listing,
                "current_price": current_price
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
                    newBid.save()
            else:
                if userBid.cleaned_data['price'] <= current_price:
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
                else:
                    newBid = Bid(price=userBid.cleaned_data['price'],listing=listing,user=request.user) 
                    newBid.save()

    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

@login_required
def close_listing(request, listing_id):
    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        listing.active = False
        bidder = listing.bids.last().user
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