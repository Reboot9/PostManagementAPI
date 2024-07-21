from django.contrib import admin

from apps.comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'text', 'is_blocked', 'created_at', 'updated_at')
    list_filter = ('author', 'is_blocked', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_editable = ('is_blocked', )
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        """
        Optimizes the queryset by using select_related to reduce the number of database queries when displaying
        the comments.
        :param request: request object
        :return: queryset with selected comments
        """
        qs = super().get_queryset(request)
        return qs.select_related('author', 'post')
