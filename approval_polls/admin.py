import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from approval_polls.models import Ballot, Choice, Poll

# Define a resource class for the User model


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "date_joined",
            "first_name",
            "last_name",
            "is_staff",
        )


# Create a custom admin class for the User model
class UserAdminWithExport(ImportExportModelAdmin):
    resource_class = UserResource
    list_display = (
        "username",
        "email",
        "date_joined",
        "first_name",
        "last_name",
        "is_staff",
    )
    ordering = ("-date_joined",)


# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, UserAdminWithExport)


class ChoiceInline(admin.TabularInline):
    """
    Defines the layout of 'Choice's in the
    admin panel.
    """

    model = Choice
    extra = 3


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    """
    Defines the layout of a 'Poll' in the
    admin panel.
    """

    fieldsets = [
        (None, {"fields": ["question"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ("id", "question", "pub_date")
    list_filter = ["pub_date"]
    search_fields = ["question"]
    actions = ["export_voters_as_csv"]

    @admin.display(description="Export poll with opt-in voter emails.")
    def export_voters_as_csv(self, queryset):
        poll_field_names = [
            "id",
            "question",
            "pub_date",
            "user",
            "vtype",
            "show_email_opt_in",
        ]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=voter_emails.csv"
        writer = csv.writer(response)

        for poll in queryset:
            writer.writerow([])
            writer.writerow(poll_field_names)
            writer.writerow([getattr(poll, field) for field in poll_field_names])
            writer.writerow([])
            ballot_field_names = ["username", "first_name", "last_name", "email"]
            writer.writerow(ballot_field_names)

            for ballot in poll.ballot_set.all():
                if ballot.permit_email:
                    if ballot.user:
                        writer.writerow(
                            [
                                getattr(ballot.user, field)
                                for field in ballot_field_names
                            ]
                        )
                    else:
                        writer.writerow(["", "", "", ballot.email])

        return response


admin.site.register(Ballot)
