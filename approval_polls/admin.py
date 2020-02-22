import csv

from django.contrib import admin
from django.http import HttpResponse

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
    list_display = ('id', 'question', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['question']
    actions = ["export_voters_as_csv"]

    def export_voters_as_csv(self, request, queryset):
        poll_field_names = [
            'id', 'question', 'pub_date', 'user', 'vtype', 'show_email_opt_in',
        ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename=voter_emails.csv'
        )
        writer = csv.writer(response)

        for poll in queryset:
            writer.writerow([])
            writer.writerow(poll_field_names)
            writer.writerow(
                [getattr(poll, field) for field in poll_field_names]
            )
            writer.writerow([])
            ballot_field_names = [
                'username', 'first_name', 'last_name', 'email'
            ]
            writer.writerow(ballot_field_names)

            for ballot in poll.ballot_set.all():
                if ballot.permit_email:
                    if ballot.user:
                        writer.writerow(
                            [getattr(
                                ballot.user, field
                            ) for field in ballot_field_names]
                        )
                    else:
                        writer.writerow(['', '', '', ballot.email])

        return response

    export_voters_as_csv.short_description = (
        'Export poll with opt-in voter emails.'
    )


admin.site.register(Poll, PollAdmin)
admin.site.register(Ballot)
