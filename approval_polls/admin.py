from django.contrib import admin

from approval_polls.models import Ballot, Choice, Poll


class ChoiceInline(admin.TabularInline):
    """
    Defines the layout of 'Choice's in the
    admin panel.
    """
    model = Choice
    extra = 3


class PollAdmin(admin.ModelAdmin):
    """
    Defines the layout of a 'Poll' in the
    admin panel.
    """
    fieldsets = [
        (None, {'fields': ['question']}),
        ('Date information', {'fields': ['pub_date'], 'classes':['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['question']


admin.site.register(Poll, PollAdmin)
admin.site.register(Ballot)
