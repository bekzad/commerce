from django import forms
from .models import User, Listing, Bid, Comment, Watchlist

class CreateListing(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'image', 'starting_price', 'category'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control','autofocus':'autofocus','autocomplete':'off'}),
            'description': forms.Textarea(attrs={'class':'form-control'}),
            'image': forms.URLInput(attrs={'class':'form-control'}),
            'starting_price': forms.NumberInput(attrs={'class':'form-control'}),
            'category': forms.Select(attrs={'class':'form-control'})
        }
        labels = {
            'image': "URL of an image (optional)",
            'starting_price': "Starting price in USD"
        }
class CreateBid(forms.ModelForm):
    class Meta:
        model = Bid
        fields = [
            'price'
        ]
        widgets = {
            'price': forms.NumberInput(attrs={'class':'form-control','placeholder':'Bid'})
        }
        labels = {
            'price': ''
        }
class CreateComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = [
            'text_comment'
        ]
        widgets = {
            'text_comment': forms.Textarea(attrs={'class':'form-control','placeholder':'Leave a comment!'}),
        }
        labels ={
            'text_comment': ''
        }