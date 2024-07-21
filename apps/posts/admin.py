from django.contrib import admin

from apps.posts.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin for Post model.
    """
    list_display = ('id', 'title', 'author',  'is_blocked', 'created_at', 'updated_at')
    list_filter = ('author', 'created_at', 'updated_at', 'is_blocked')
    date_hierarchy = 'created_at'
    search_fields = ('title', 'author__username', 'author__email')
    list_editable = [
        'is_blocked',
    ]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'content')
        }),
        ('Author and Status', {
            'fields': ('author', 'is_blocked', 'auto_reply_enabled', 'auto_reply_delay',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
