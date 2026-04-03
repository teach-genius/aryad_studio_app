"""
models.py — ARYAD Web App
=========================
Tables:
  1. Visitor            — visiteur anonyme (UUID persistant localStorage)
  2. Conversation       — session de chat unique par visiteur (UUID PK)
  3. Message            — message individuel (user | bot)
  4. ConversationMemory — fenêtre glissante des 4 derniers messages (contexte LLM)
  5. HeroContent        — section Hero éditable
  6. Solution           — cartes solutions
  7. ProcessStep        — étapes du processus
  8. Technology         — badges technologies (filtrable par catégorie)
  9. SiteConfig         — singleton : CTA, About, footer, chatbot
"""

import uuid
from django.db import models
from django.utils import timezone 

# ══════════════════════════════════════════════════════════
#  1. VISITOR
# ══════════════════════════════════════════════════════════

class Visitor(models.Model):

    class DeviceType(models.TextChoices):
        DESKTOP = 'desktop', 'Desktop'
        MOBILE  = 'mobile',  'Mobile'
        TABLET  = 'tablet',  'Tablet'
        UNKNOWN = 'unknown', 'Unknown'

    # Identifiant persistant côté client (localStorage)
    uid = models.UUIDField(
        default=uuid.uuid4, unique=True, db_index=True,
        help_text="UUID généré côté client, persisté en localStorage"
    )

    # Géolocalisation
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    country      = models.CharField(max_length=100, blank=True, default='')
    country_code = models.CharField(max_length=4,   blank=True, default='')
    city         = models.CharField(max_length=100, blank=True, default='')
    region       = models.CharField(max_length=100, blank=True, default='')
    time_zone     = models.CharField(max_length=60,  blank=True, default='')
    latitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Device & navigateur
    device_type   = models.CharField(max_length=10, choices=DeviceType.choices, default=DeviceType.UNKNOWN)
    user_agent    = models.TextField(blank=True, default='')
    browser       = models.CharField(max_length=60, blank=True, default='')
    os            = models.CharField(max_length=60, blank=True, default='')
    screen_width  = models.PositiveIntegerField(null=True, blank=True)
    screen_height = models.PositiveIntegerField(null=True, blank=True)
    language      = models.CharField(max_length=20, blank=True, default='')

    # Navigation & UTM
    referrer     = models.URLField(max_length=500, blank=True, default='')
    landing_page = models.CharField(max_length=200, blank=True, default='')
    utm_source   = models.CharField(max_length=100, blank=True, default='')
    utm_medium   = models.CharField(max_length=100, blank=True, default='')
    utm_campaign = models.CharField(max_length=100, blank=True, default='')

    # Timestamps
    first_seen  = models.DateTimeField(default=timezone.now)
    last_seen   = models.DateTimeField(auto_now=True)
    visit_count = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name        = 'Visiteur'
        verbose_name_plural = 'Visiteurs'
        ordering            = ['-first_seen']
        indexes = [
            models.Index(fields=['uid']),
            models.Index(fields=['country_code']),
            models.Index(fields=['first_seen']),
        ]

    def __str__(self):
        loc = f"{self.city}, {self.country}" if self.city else self.country or "Lieu inconnu"
        return f"Visiteur {str(self.uid)[:8]}… — {loc} ({self.device_type})"

    def update_last_seen(self):
        self.visit_count += 1
        self.save(update_fields=['last_seen', 'visit_count'])


# ══════════════════════════════════════════════════════════
#  2. CONVERSATION
# ══════════════════════════════════════════════════════════

class Conversation(models.Model):

    class Status(models.TextChoices):
        ACTIVE   = 'active',   'Active'
        CLOSED   = 'closed',   'Fermée'
        ARCHIVED = 'archived', 'Archivée'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='conversations')
    status  = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    started_at    = models.DateTimeField(default=timezone.now)
    updated_at    = models.DateTimeField(auto_now=True)
    ended_at      = models.DateTimeField(null=True, blank=True)
    message_count = models.PositiveIntegerField(default=0)
    summary       = models.TextField(blank=True, default='')

    class Meta:
        verbose_name        = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering            = ['-started_at']
        indexes = [
            models.Index(fields=['visitor', 'status']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"Conv {str(self.id)[:8]}… [{self.status}] — {self.visitor}"

    def close(self):
        self.status   = self.Status.CLOSED
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at'])

    def increment_count(self):
        self.message_count += 1
        self.save(update_fields=['message_count', 'updated_at'])


# ══════════════════════════════════════════════════════════
#  3. MESSAGE
# ══════════════════════════════════════════════════════════

class Message(models.Model):

    class Role(models.TextChoices):
        USER = 'user', 'Utilisateur'
        BOT  = 'bot',  'Bot'

    conversation     = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role             = models.CharField(max_length=4, choices=Role.choices)
    content          = models.TextField()
    created_at       = models.DateTimeField(default=timezone.now)
    response_time_ms = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Message'
        verbose_name_plural = 'Messages'
        ordering            = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        preview = self.content[:60] + '…' if len(self.content) > 60 else self.content
        return f"[{self.role.upper()}] {preview}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.conversation.increment_count()


# ══════════════════════════════════════════════════════════
#  4. CONVERSATION MEMORY
# ══════════════════════════════════════════════════════════

class ConversationMemory(models.Model):
    """
    Fenêtre glissante des N derniers messages.

    context_window (JSONField) :
    [
        {"role": "user", "content": "..."},
        {"role": "bot",  "content": "..."},
        ...  max MEMORY_SIZE entrées
    ]

    Injectée dans chaque appel LLM comme contexte conversationnel.
    """

    MEMORY_SIZE = 4  # 2 échanges user/bot

    conversation = models.OneToOneField(
        Conversation, on_delete=models.CASCADE,
        related_name='memory', primary_key=True
    )
    context_window    = models.JSONField(default=list)
    long_term_summary = models.TextField(blank=True, default='')
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Mémoire de conversation'
        verbose_name_plural = 'Mémoires de conversations'

    def __str__(self):
        return f"Mémoire {str(self.conversation_id)[:8]}… ({len(self.context_window)} msgs)"

    def push(self, role: str, content: str):
        """Ajoute un message et maintient la fenêtre à MEMORY_SIZE."""
        self.context_window.append({"role": role, "content": content})
        if len(self.context_window) > self.MEMORY_SIZE:
            self.context_window = self.context_window[-self.MEMORY_SIZE:]
        self.save(update_fields=['context_window', 'updated_at'])

    def get_context(self) -> list:
        """Retourne la fenêtre pour injection LLM."""
        return list(self.context_window)

    def reset(self):
        self.context_window = []
        self.save(update_fields=['context_window', 'updated_at'])


# ══════════════════════════════════════════════════════════
#  5. HERO CONTENT
# ══════════════════════════════════════════════════════════

class HeroContent(models.Model):
    badge_text          = models.CharField(max_length=100, default='Disponible pour de nouveaux projets')
    title_thin          = models.CharField(max_length=100, default='Intelligence artificielle')
    title_grad          = models.CharField(max_length=100, default='& architecture')
    title_outline       = models.CharField(max_length=100, default='logicielle')
    subtitle            = models.TextField(default='')
    cta_primary_label   = models.CharField(max_length=60,  default='Explorer les solutions')
    cta_primary_href    = models.CharField(max_length=100, default='#solutions')
    cta_secondary_label = models.CharField(max_length=60,  default='Collaborer avec nous')
    cta_secondary_href  = models.CharField(max_length=100, default='#cta')
    is_active           = models.BooleanField(default=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Contenu Hero'
        verbose_name_plural = 'Contenus Hero'

    def __str__(self):
        return f"Hero — {self.title_thin} / {self.title_grad}"


# ══════════════════════════════════════════════════════════
#  6. SOLUTION
# ══════════════════════════════════════════════════════════

class Solution(models.Model):
    icon        = models.ImageField(upload_to="icons/", null=True, blank=True)
    title       = models.CharField(max_length=100)
    description = models.TextField()
    tag         = models.CharField(max_length=60, default='En savoir plus →')
    is_featured = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = 'Solution'
        verbose_name_plural = 'Solutions'
        ordering            = ['order']

    def __str__(self):
        return self.title


# ══════════════════════════════════════════════════════════
#  7. PROCESS STEP
# ══════════════════════════════════════════════════════════

class ProcessStep(models.Model):
    number      = models.CharField(max_length=2, default='01')
    title       = models.CharField(max_length=100)
    description = models.TextField()
    order       = models.PositiveSmallIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        verbose_name        = "Étape du processus"
        verbose_name_plural = "Étapes du processus"
        ordering            = ['order']

    def __str__(self):
        return f"{self.number} — {self.title}"


# ══════════════════════════════════════════════════════════
#  8. TECHNOLOGY
# ══════════════════════════════════════════════════════════

class Technology(models.Model):

    class Category(models.TextChoices):
        AI    = 'ai',    'IA & ML'
        WEB   = 'web',   'Web & Mobile'
        CLOUD = 'cloud', 'Cloud & DevOps'

    icon      = models.ImageField(upload_to="icons/", null=True, blank=True)
    name      = models.CharField(max_length=60)
    category  = models.CharField(max_length=10, choices=Category.choices)
    order     = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Technologie'
        verbose_name_plural = 'Technologies'
        ordering            = ['category', 'order']

    def __str__(self):
        return f"{self.icon} {self.name} [{self.get_category_display()}]"


# ══════════════════════════════════════════════════════════
#  9. SITE CONFIG  (singleton)
# ══════════════════════════════════════════════════════════

class SiteConfig(models.Model):
    """Un seul enregistrement actif — accès via SiteConfig.get()."""

    # About
    about_eyebrow = models.CharField(max_length=60,  default="À propos d'ARYAD")
    about_title   = models.TextField(default='Un studio IA de nouvelle génération.')
    about_para1   = models.TextField(default='')
    about_para2   = models.TextField(default='', blank=True)

    # CTA
    cta_eyebrow      = models.CharField(max_length=60,  default='Travaillons ensemble')
    cta_title        = models.TextField(default='')
    cta_subtitle     = models.TextField(default='')
    cta_button_label = models.CharField(max_length=80,  default='Planifier un appel stratégique')
    cta_button_href  = models.CharField(max_length=200, default='mailto:contact@aryad.ai')
    cta_note         = models.CharField(max_length=120, default='Réponse sous 24h · Première consultation gratuite')

    # Contact & réseaux
    email        = models.EmailField(default='contact@aryad.ai')
    linkedin_url = models.URLField(blank=True, default='')
    github_url   = models.URLField(blank=True, default='')

    # Footer
    footer_tagline = models.CharField(max_length=100, default='Systèmes intelligents. Résultats concrets.')
    footer_status  = models.CharField(max_length=80,  default='Disponible · Nouveaux projets')

    # Chatbot
    chatbot_greeting    = models.TextField(
        default="Bonjour 👋 Je suis l'assistant ARYAD.\nComment puis-je vous aider aujourd'hui ?"
    )
    chatbot_suggestions = models.JSONField(
        default=list,
        help_text='Ex: ["Voir les solutions IA", "Planifier un appel"]'
    )

    is_active  = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Configuration du site'
        verbose_name_plural = 'Configuration du site'

    def __str__(self):
        return f"SiteConfig (màj {self.updated_at.strftime('%d/%m/%Y %H:%M')})"

    @classmethod
    def get(cls):
        config, _ = cls.objects.get_or_create(is_active=True)
        return config