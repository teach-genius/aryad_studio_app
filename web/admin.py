from django.contrib import admin
from .models import (
    Visitor,
    Conversation,
    Message,
    ConversationMemory,
    HeroContent,
    Solution,
    ProcessStep,
    Technology,
    SiteConfig
)

# ══════════════════════════════════════════════════════════
#  1. VISITOR
# ══════════════════════════════════════════════════════════

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = (
        "short_uid",
        "country",
        "city",
        "device_type",
        "visit_count",
        "first_seen",
        "last_seen",
    )
    list_filter = ("device_type", "country_code", "first_seen")
    search_fields = ("uid", "country", "city", "ip_address")
    readonly_fields = ("uid", "first_seen", "last_seen")
    ordering = ("-first_seen",)

    def short_uid(self, obj):
        return str(obj.uid)[:8]
    short_uid.short_description = "UID"


# ══════════════════════════════════════════════════════════
#  2. MESSAGE INLINE
# ══════════════════════════════════════════════════════════

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("role", "content", "response_time_ms", "created_at")
    ordering = ("created_at",)


# ══════════════════════════════════════════════════════════
#  3. CONVERSATION
# ══════════════════════════════════════════════════════════

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "short_id",
        "visitor",
        "status",
        "message_count",
        "started_at",
        "ended_at",
    )
    list_filter = ("status", "started_at")
    search_fields = ("id", "visitor__uid")
    readonly_fields = ("id", "started_at", "updated_at", "message_count")
    inlines = [MessageInline]
    ordering = ("-started_at",)

    def short_id(self, obj):
        return str(obj.id)[:8]
    short_id.short_description = "ID"


# ══════════════════════════════════════════════════════════
#  4. MESSAGE
# ══════════════════════════════════════════════════════════

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "short_content", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content", "conversation__id")
    readonly_fields = ("created_at",)

    def short_content(self, obj):
        return obj.content[:80] + "…" if len(obj.content) > 80 else obj.content
    short_content.short_description = "Contenu"


# ══════════════════════════════════════════════════════════
#  5. CONVERSATION MEMORY
# ══════════════════════════════════════════════════════════

@admin.register(ConversationMemory)
class ConversationMemoryAdmin(admin.ModelAdmin):
    list_display = ("conversation", "window_size", "updated_at")
    readonly_fields = ("updated_at",)
    search_fields = ("conversation__id",)

    def window_size(self, obj):
        return len(obj.context_window)
    window_size.short_description = "Nb messages mémoire"


# ══════════════════════════════════════════════════════════
#  6. HERO CONTENT
# ══════════════════════════════════════════════════════════

@admin.register(HeroContent)
class HeroContentAdmin(admin.ModelAdmin):
    list_display = ("title_thin", "title_grad", "is_active", "updated_at")
    list_filter = ("is_active",)
    readonly_fields = ("updated_at",)


# ══════════════════════════════════════════════════════════
#  7. SOLUTION
# ══════════════════════════════════════════════════════════

@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
    list_display = ("icon", "title", "is_featured", "is_active", "order")
    list_filter = ("is_featured", "is_active")
    search_fields = ("title", "description")
    ordering = ("order",)


# ══════════════════════════════════════════════════════════
#  8. PROCESS STEP
# ══════════════════════════════════════════════════════════

@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "is_active", "order")
    list_filter = ("is_active",)
    ordering = ("order",)


# ══════════════════════════════════════════════════════════
#  9. TECHNOLOGY
# ══════════════════════════════════════════════════════════

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("icon", "name", "category", "is_active", "order")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    ordering = ("category", "order")


# ══════════════════════════════════════════════════════════
#  10. SITE CONFIG (SINGLETON)
# ══════════════════════════════════════════════════════════

@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ("updated_at", "is_active")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        # Empêche d’avoir plusieurs configurations
        if SiteConfig.objects.exists():
            return False
        return True