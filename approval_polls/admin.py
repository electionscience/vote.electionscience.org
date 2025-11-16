import csv

from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from approval_polls.models import Ballot, Choice, Poll, VoteInvitation

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


class VoteInvitationInline(admin.TabularInline):
    """
    Defines the layout of 'VoteInvitation's in the
    admin panel.
    """

    model = VoteInvitation
    extra = 0
    readonly_fields = ("key", "sent_date", "ballot")
    fields = ("email", "key", "sent_date", "ballot")


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    """
    Defines the layout of a 'Poll' in the
    admin panel.
    """

    fieldsets = [
        (None, {"fields": ["question"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
        ("Visibility", {"fields": ["is_private"]}),
    ]
    inlines = [ChoiceInline, VoteInvitationInline]
    list_display = ("id", "question", "pub_date", "is_private")
    list_filter = ["pub_date", "is_private"]
    search_fields = ["question"]
    actions = ["export_voters_as_csv", "make_private", "make_public"]

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

    @admin.action(description="Mark selected polls as private (hide from front page)")
    def make_private(self, request, queryset):
        updated = queryset.update(is_private=True)
        self.message_user(
            request,
            f"{updated} poll(s) marked as private and hidden from front page.",
        )

    @admin.action(description="Mark selected polls as public (show on front page)")
    def make_public(self, request, queryset):
        updated = queryset.update(is_private=False)
        self.message_user(
            request,
            f"{updated} poll(s) marked as public and shown on front page.",
        )


admin.site.register(Ballot)


@admin.register(VoteInvitation)
class VoteInvitationAdmin(admin.ModelAdmin):
    """
    Defines the layout of a 'VoteInvitation' in the admin panel.
    """

    list_display = ("email", "poll", "sent_date", "has_ballot")
    list_filter = ["sent_date", "poll"]
    search_fields = ["email", "poll__question"]
    readonly_fields = ("key",)

    def has_ballot(self, obj):
        return obj.ballot is not None

    has_ballot.boolean = True
    has_ballot.short_description = "Voted"
