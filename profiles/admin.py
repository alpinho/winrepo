from django.contrib import admin
from django.apps import apps

from .models import User, Profile, Recommendation, Country, Publication


class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_under_represented')


class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'reviewer_name', 'reviewer_email', 'comment')
    search_fields = ('profile__name', 'reviewer_name',
                     'reviewer_email', 'comment')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'name', 'email', '_has_profile')
    search_fields = ('username', 'name', 'email')

    def _has_profile(self, obj):
        return obj.profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'institution')
    search_fields = ('name', 'institution', 'email', 'is_public')


class PublicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'authors', 'journal_issue', 'published_at', 'doi')
    search_fields = ('title', 'authors', 'journal_issue', 'published_at', 'doi')


admin.site.site_header = 'WiNRepo Admin'

for model in apps.get_models():
    if model.__name__ and admin.site.is_registered(model):
        admin.site.unregister(model)

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Publication, PublicationAdmin)
