from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView, 
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.forms import inlineformset_factory
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import CommentForm
from .models import *


class Index(ListView):
    model = Listing
    template_name = 'auctions/index.html'
    context_object_name = 'listings'
    ordering = ['-date_created']

def index(request):
    listings = Listing.objects.filter(status='Active')

    context = {
        'listings': listings
    }
    return render(request, 'auctions/index.html', context)

def category(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, "auctions/categories.html", context)

def category_listings(request, id):
    listings = Listing.objects.filter(category=id).order_by('-id')
    category = Category.objects.get(id=id)
   
    context = {
        'listings': listings,
        'category': category
    }
    return render(request, "auctions/category_listings.html", context)

class CommentListView(ListView):
    model = Comment
    template_name = 'auctions/comments.html'
    context_object_name = 'comments'
    ordering = ['-date_created']

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

def listing_detail(request, pk):
    listing = Listing.objects.get(id=pk)
    comments = Comment.objects.filter(post=listing)
    user = request.user
    bids = Bid.objects.filter(listing=listing).order_by('-amount')

    won = Bid.objects.filter(winner=True)
    for win in won:
        if listing == win.listing:
            won = True
        else:
            won = False

    watchlist = Watchlist.objects.filter(user=user)
    for l in watchlist:
        if listing == l.listing:
            listing.in_watchlist = True

    if listing.status == 'Not Active':
        inactive = True
    else:
        inactive = False

    if request.method == "POST":
        if 'comment' in request.POST:
            form = CommentForm(request.POST or None)
            if form.is_valid():
                author = user
                content = form.cleaned_data["content"]

                s = Comment.objects.create(
                    author = author,
                    content = content,
                    post = listing
                )
                s.save()
                return HttpResponseRedirect(reverse("listing-detail", args=(pk,)))
        elif 'bid' in request.POST:
            amount = request.POST['amount']
            price = listing.current_price    
            if float(amount) <= float(price):
                messages.error(request, 'Bid must be greater than current price')
                return HttpResponseRedirect(reverse("listing-detail", args=(pk,)))
            else:
                bid = Bid.objects.create(listing=listing, user=user, amount=amount)
                bid.save()

            if float(amount) > float(price):
                    listing.current_price = float(amount)
                    listing.save()

        elif 'watchlist' in request.POST:
            watchlist = Watchlist.objects.create(user=user, listing=listing)
            watchlist.save()
            return HttpResponseRedirect(reverse("listing-detail", args=(pk,)))

        elif 'watchlist-remove' in request.POST:
            watchlist = Watchlist.objects.get(user=user, listing=listing)
            watchlist.delete()
            return HttpResponseRedirect(reverse("listing-detail", args=(pk,)))

        elif 'listing-close' in request.POST:
            for bid in bids:
                if bid.amount == listing.current_price:
                    bid.winner = True
                    bid.save()
            listing.status = 'Not Active'
            listing.save()
            return HttpResponseRedirect(reverse("listing-detail", args=(pk,)))

    context = {
        'listing': listing,
        'comments': comments,
        'inactive': inactive,
        'form': CommentForm(),
        'bids': bids,
        'won': won
    }
    return render(request, "auctions/listing_detail.html", context)

def userListings(request, pk):
    user = User.objects.get(id=pk)
    active = Listing.objects.filter(author=user, status='Active')
    inactive = Listing.objects.filter(author=user, status='Not Active')
    context = {
        'active': active,
        'inactive': inactive
    }
    return render(request, 'auctions/user_listings.html', context)

def winnings(request, pk):
    user = User.objects.get(id=pk)
    try:
        winnings = Bid.objects.filter(user=user, winner=True)
    except: 
        winnings = {}

    context = {
        'winnings': winnings
    }
    return render(request, 'auctions/winnings.html', context)

class ListingDetailView(DetailView):
    model = Listing
        
    def get_context_data(self, **kwargs):
        self.listing = get_object_or_404(Listing, name=self.kwargs['listing'])
        comment = Comment.objects.filter(post=self.listing).order_by('-id')
        context = super().get_context_data(**kwargs)
        context['comments'] = comment
        return context

class ListingCreateView(LoginRequiredMixin, CreateView):
    model = Listing
    fields = ['title', 'description', 'current_price', 'image', 'category', 'status']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    fields = ['title', 'description', 'image', 'category', 'status']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        listing = self.get_object()
        if self.request.user == listing.author:
            return True
        return False

class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    success_url = '/'

    def test_func(self):
        listing = self.get_object()
        if self.request.user == listing.author:
            return True
        return False

def watchlist(request, pk):
    user = User.objects.get(id=pk)
    watchlist = Watchlist.objects.filter(user=user)

    context = {
        'watchlist': watchlist
    }
    return render(request, 'auctions/watchlist.html', context)

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



