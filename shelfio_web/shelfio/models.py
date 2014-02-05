import random
import string
import hashlib

from shelfio import utils
from shelfio import indexer
from shelfio.fields import UUIDField

from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import TextInput
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save


FORMAT_CHOICES = (('book', 'Book'),
                            ('Video/Film', 'Video'),
                            ('Sound Recording', 'Music'),
                            ('webpage', 'Webpage'))

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    display_welcome = models.BooleanField(default=True)
    favorites_are_private = models.BooleanField(default=False)
    gravatar_enabled = models.BooleanField(default=False)
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
        # We want an auth token for each user. Seems like a handy spot, so lets do that here.
        auth_token = AuthTokens(user=instance)
        auth_token.save()

post_save.connect(create_user_profile, sender=User)

class AuthTokens(models.Model):
    user = models.ForeignKey(User)
    token = UUIDField(auto=True)
    notes = models.CharField(max_length=400)
    is_active = models.BooleanField(default=True)

class Shelf(models.Model):
    user = models.ForeignKey(User)
    shelf_uuid = UUIDField(auto=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.CharField(max_length=1000)
    creation_date = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        if Shelf.objects.filter(user=self.user, slug=slug).exclude(pk=self.pk).exists():
            raise ValidationError('You already have a shelf by that name.')
        else:
            self.slug = slugify(self.name)
            super(Shelf, self).save(*args, **kwargs)
            
        # We want items to be searchable through elastic search, pass the data off to our indexer
        if not self.is_private:
            indexer.index_shelf(self)
            
    def delete(self, *args, **kwargs):
        super(Shelf, self).delete(*args, **kwargs)
        indexer.unindex_shelf(self)
        #TODO: Delete items on the shelf if shelf is deleted 

class Item(models.Model):
    shelf = models.ForeignKey(Shelf)
    item_uuid = UUIDField(auto=True)
    title = models.CharField(max_length=200)
    link = models.URLField(max_length=2000)
    measurement_page_numeric = models.PositiveIntegerField(default=300)
    measurement_height_numeric = models.DecimalField(default='25.5', max_digits=5, decimal_places=2)
    format = models.CharField(max_length=200, default='book')
    shelfrank = models.PositiveIntegerField(default=random.randint(1, 99))
    creation_date = models.DateTimeField(auto_now=True)
    pub_date = models.PositiveIntegerField(default=utils.get_current_year())
    isbn = models.CharField(max_length=200, null=True, blank=True)
    notes = models.CharField(max_length=2000, null=True, blank=True)
    sort_order = models.PositiveIntegerField(editable=False) 

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            try:
                max = Item.objects.order_by('-sort_order')[0].sort_order
                self.sort_order = max + 1
            except IndexError:
                self.sort_order = 1
        super(Item, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Item, self).delete(*args, **kwargs)
        indexer.unindex_item(self)
        
    class Meta:
        ordering = ['-sort_order']
        models.CharField(max_length=200)   
    
class Creator(models.Model):
    item = models.ForeignKey(Item)
    creator_uuid = UUIDField(auto=True)
    name = models.CharField(max_length=200)
    
    def save(self, *args, **kwargs):
        super(Creator, self).save(*args, **kwargs)
    
        # We want items to be searchable through elastic search, pass the data off to our indexer
        if not self.item.shelf.is_private:
            indexer.index_item(self.item)

    
    def __unicode__(self):
        return self.name
    
class FavoriteUser(models.Model):
    """Users can favorite (or follow or star) another user"""
    
    favorite_user_uuid = UUIDField(auto=True)
    follower = models.ForeignKey(User, related_name='user_follower')
    leader = models.ForeignKey(User, related_name='user_leader    ')
    
    def save(self, *args, **kwargs):
        if FavoriteUser.objects.filter(follower=self.follower, leader=self.leader).exclude(pk=self.pk).exists():
            raise ValidationError('You have already favorited that user.')
        else:
            super(FavoriteUser, self).save(*args, **kwargs)
    
class FavoriteShelf(models.Model):
    """Users can favorite (or follow or star) a shelf"""
    
    favorite_shelf_uuid = UUIDField(auto=True)
    user = models.ForeignKey(User)
    shelf = models.ForeignKey(Shelf)
    
    def save(self, *args, **kwargs):
        if FavoriteShelf.objects.filter(user=self.user, shelf=self.shelf).exclude(pk=self.pk).exists():
            raise ValidationError('You have already favorited that shelf.')
        else:
            super(FavoriteShelf, self).save(*args, **kwargs)    

    
#Forms:
class AddToShelfConfirmForm(forms.Form):
    shelf = forms.ModelChoiceField(queryset=Shelf.objects.all())
    title = forms.CharField(max_length=300)
    author = forms.CharField(max_length=100)
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=100)
    
class UserRegForm(forms.ModelForm):
    """
    stripped down user reg form
    This is mostly a django.contrib.auth.forms.UserCreationForm
    """
    error_messages = {
        'duplicate_username': "A user with that username already exists.",
        'duplicate_email': "A user with that email address already exists.",
    }
    username = forms.RegexField(label="Username", max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text = "30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only.",
        error_messages = {
            'invalid': "This value may contain only letters, numbers and "
                         "@/./+/-/_ characters."})
    
    email = forms.RegexField(label="Email", required=True, max_length=254,
        regex=r'^[\w.@+-]+$',
        help_text = "Letters, digits and @/./+/-/_ only. 254 characters or fewer.",
        error_messages = {
            'invalid': "This value may contain only letters, numbers and "
                         "@/./+/-/_ characters."})
    
    
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])
    
    def clean_email(self):
        # Since User.email is unique, this check is redundant,
        # but it sets a nicer error message than the ORM.
        
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def save(self, commit=True):
        user = super(UserRegForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class EmailInput(TextInput):
    input_type = 'email'

class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(required=False, widget=EmailInput)

class NewShelfForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={'rows': '4'}),
    )
    is_private = forms.BooleanField(required=False)

class AddItemForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(AddItemForm, self).__init__(*args, **kwargs)
        if user is not None:
            self.fields['shelf'].queryset = Shelf.objects.filter(user=user)
            self.fields['shelf'].empty_label = None
    class Meta:
        model = Item
        widgets = { 'shelfrank' : forms.HiddenInput(),
                   'format' : forms.Select(choices=FORMAT_CHOICES),
                   'pub_date' : forms.TextInput(attrs={'size':4, 'maxlength':4}),
                   'notes': forms.Textarea(attrs={'rows': '4'}) }

class CreatorForm(forms.Form):
    creator = forms.CharField(max_length=1000)