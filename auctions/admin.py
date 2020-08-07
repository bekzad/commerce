from django.contrib import admin

from .models import User, Listing, Bid, Comment, Watchlist

class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'active')

class BidAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'price')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'text_comment')

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'active')

# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Watchlist, WatchlistAdmin)