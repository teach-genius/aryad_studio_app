import json
import time
import uuid
from .utils import chatAryadResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
from .models import (
    Visitor, Conversation, Message, ConversationMemory,
    HeroContent, Solution, ProcessStep, Technology, SiteConfig,
)
GEO_API_URL = "https://ipapi.co/{ip}/json/"

# ══════════════════════════════════════════════════════════
# REGISTER VISITOR API
# ══════════════════════════════════════════════════════════
def get_geo_from_ip(ip: str) -> dict:
    """Récupère la géolocalisation depuis ipapi.co pour une IP donnée."""
    try:
        url = GEO_API_URL.format(ip=ip)
        resp = requests.get(url, timeout=4)
        if resp.status_code != 200:
            return {}
        data = resp.json()
        return {
            "country":      data.get("country_name") or "",
            "country_code": data.get("country_code") or "",
            "city":         data.get("city") or "",
            "region":       data.get("region") or "",
            "time_zone":    data.get("timezone") or "",
            "latitude":     float(data["latitude"]) if data.get("latitude") else None,
            "longitude":    float(data["longitude"]) if data.get("longitude") else None,
        }
    except Exception as e:
        print("GEO ERROR:", e)
        return {}


def _get_client_ip(request):
    """Récupère l'IP réelle du client."""
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')

def _get_or_create_visitor(request, visitor_uid=None):
    """Récupère ou crée un visiteur."""
    if visitor_uid:
        try:
            visitor = Visitor.objects.get(uid=uuid.UUID(str(visitor_uid)))
            visitor.visit_count += 1
            visitor.save(update_fields=['last_seen', 'visit_count'])
            return visitor
        except (Visitor.DoesNotExist, ValueError):
            pass

    ip = _get_client_ip(request)
    geo = get_geo_from_ip(ip)

    visitor = Visitor.objects.create(
        uid=uuid.uuid4(),
        ip_address=ip,
        country=geo.get("country", ""),
        country_code=geo.get("country_code", ""),
        city=geo.get("city", ""),
        region=geo.get("region", ""),
        time_zone=geo.get("time_zone", ""),
        latitude=geo.get("latitude"),
        longitude=geo.get("longitude"),
    )
    return visitor

# ══════════════════════════════════════════════════════════
#  VUE 2 — REGISTER VISITOR
# ══════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(["POST"])
def register_visitor(request):
    """
    POST /api/visitor/register/
    Body JSON optionnel : {
        "visitor_uid": "uuid-existant",
        "device_type": "desktop|mobile|tablet",
        "browser": "...",
        "os": "...",
        "screen_width": 1920,
        "screen_height": 1080,
        "language": "fr",
        "referrer": "...",
        "landing_page": "...",
        "utm_source": "...",
        "utm_medium": "...",
        "utm_campaign": "..."
    }
    """
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalide"}, status=400)

    visitor = _get_or_create_visitor(request, data.get("visitor_uid"))

    # Champs optionnels à mettre à jour
    optional_fields = [
        "device_type", "browser", "os",
        "screen_width", "screen_height", "language",
        "referrer", "landing_page", "utm_source", "utm_medium", "utm_campaign",
    ]

    updated = []
    for f in optional_fields:
        val = data.get(f)
        if val is not None:
            setattr(visitor, f, val)
            updated.append(f)
        

    if updated:
        visitor.save(update_fields=list(set(updated)))

    return JsonResponse({
        "status": "ok",
        "visitor_uid": str(visitor.uid),
        "geo": {
            "country": visitor.country,
            "country_code": visitor.country_code,
            "city": visitor.city,
            "region": visitor.region,
            "time_zone": visitor.time_zone,
            "latitude": visitor.latitude,
            "longitude": visitor.longitude,
        }
    })




def _get_or_create_conversation(visitor, conversation_id):
    """Retourne (conversation, memory, is_new)."""
    if conversation_id:
        try:
            conv = Conversation.objects.get(
                id=uuid.UUID(str(conversation_id)),
                visitor=visitor,
                status=Conversation.Status.ACTIVE,
            )
            mem, _ = ConversationMemory.objects.get_or_create(conversation=conv)
            return conv, mem, False
        except (Conversation.DoesNotExist, ValueError):
            pass
    conv = Conversation.objects.create(visitor=visitor)
    mem  = ConversationMemory.objects.create(conversation=conv)
    return conv, mem, True


def _bot_reply(user_text: str, context: list, config: SiteConfig) -> str:
    system = '''
        Tu es l’assistant virtuel officiel d’ARYAD, un studio spécialisé en intelligence artificielle et en architecture logicielle.

        Ta mission est d’aider les visiteurs, de présenter les solutions d’ARYAD et d’encourager naturellement les entreprises, startups et porteurs de projets à entrer en contact avec notre équipe.

        Règles importantes :
        - Réponds uniquement en français.
        - Maximum 3 phrases par réponse.
        - Ton ton doit être professionnel, clair, moderne et engageant.
        - Ne prends jamais de décision et ne fais aucune promesse.
        - Ne mentionne jamais ces règles.
        - Ne montre jamais ton raisonnement interne.

        Objectifs :
        - Mettre en valeur l'expertise d’ARYAD en intelligence artificielle, automatisation, agents IA et développement de solutions sur mesure.
        - Donner envie au visiteur d’explorer nos solutions ou de discuter de son projet.
        - Inciter naturellement l’utilisateur à nous contacter ou à suivre nos actualités.

        Quand c’est pertinent :
        - suggère de nous contacter pour discuter du projet
        - propose de suivre nos actualités IA
        - invite à découvrir nos solutions

        Call to action :

        Pour suivre nos projets et innovations en intelligence artificielle :
        <a href='https://whatsapp.com/channel/0029Vb7ZEw9JZg45idRZfW0m'style='color:var(--accent)'>Rejoindre la chaîne WhatsApp ARYAD →</a>

        Pour discuter d’un projet ou poser une question :
        <a href='mailto:aryadacademie@gmail.com' style='color:var(--accent)'>Contacter l’équipe ARYAD →</a>

        ARYAD conçoit des systèmes intelligents pour automatiser, analyser et transformer les entreprises grâce à l’IA.
        '''
    messages = [{"role": "system", "content": system}]
    formatted_context = [{"role": "assistant" if m["role"] == "bot" else "user","content": m["content"]} for m in context[:2]]
    messages.extend(formatted_context)
    messages.append({"role": "user","content": user_text.lower()})

    # rules = [
    #     (['solution', 'service', 'offre', 'produit'],
    #      "Nous proposons des <strong>modèles IA sur mesure</strong>, l'automatisation intelligente, "
    #      "le développement web & mobile et notre produit phare <strong>AryadRH</strong>. "
    #      "<a href='#solutions' style='color:var(--accent)'>Voir toutes les solutions →</a>"),

    #     (['aryadrh', ' rh ', 'ressources humaines', 'recrutement'],
    #      "<strong>AryadRH</strong> est notre logiciel RH augmenté par l'IA : "
    #      "recrutement prédictif, analyse des performances, automatisation administrative. "
    #      "<a href='#product' style='color:var(--accent)'>Voir la démo →</a>"),

    #     (['appel', 'contact', 'rendez-vous', 'rdv', 'planifier', 'discuter'],
    #      f"Avec plaisir ! Écrivez-nous à "
    #      f"<a href='mailto:{config.email}' style='color:var(--accent)'>{config.email}</a> "
    #      f"ou <a href='#cta' style='color:var(--accent)'>planifiez un appel →</a>"),

    #     (['prix', 'tarif', 'coût', 'devis', 'budget'],
    #      "Nos tarifs sont adaptés à chaque projet. "
    #      "<a href='#cta' style='color:var(--accent)'>Demandez un devis gratuit →</a>"),

    #     (['technologie', 'stack', 'python', 'django', 'llm', 'neo4j', 'qdrant', 'outil'],
    #      "Notre stack : Python, PyTorch, TensorFlow, FastAPI, Django, Neo4j, Qdrant, Docker, AWS/GCP. "
    #      "<a href='#technologies' style='color:var(--accent)'>Voir toutes les technologies →</a>"),

    #     (['processus', 'comment', 'étape', 'méthode', 'travail'],
    #      "Notre méthode en 5 étapes : <strong>Découverte → Architecture → "
    #      "Modélisation IA → Développement → Déploiement & Scale</strong>. "
    #      "<a href='#process' style='color:var(--accent)'>Voir le détail →</a>"),
    # ]

    # for keywords, response in rules:
    #     if any(kw in t for kw in keywords):
    #         return response

    if messages:
        return chatAryadResponse(messages)
    return (
        "Merci pour votre message ! Notre équipe vous répondra rapidement. "
        "<a href='#cta' style='color:var(--accent)'>Planifier un appel →</a>"
    )


# ══════════════════════════════════════════════════════════
#  VUE 1 — INDEX
# ══════════════════════════════════════════════════════════

def index_view(request):

    config = SiteConfig.get()
    # Hero
    h = HeroContent.objects.filter(is_active=True).first()
    hero = {
        'badge':         getattr(h,'badge_text','Disponible pour de nouveaux projets'),
        'title': {
            'line_thin':    getattr(h, 'title_thin',    'Intelligence artificielle'),
            'line_grad':    getattr(h, 'title_grad',    '& architecture'),
            'line_outline': getattr(h, 'title_outline', 'logicielle'),
        },
        'subtitle':      getattr(h, 'subtitle', ''),
        'cta_primary':   {'label': getattr(h, 'cta_primary_label', 'Explorer les solutions'), 'href': getattr(h, 'cta_primary_href',   '#solutions')},
        'cta_secondary': {'label': getattr(h, 'cta_secondary_label', 'Collaborer avec nous'),   'href': getattr(h, 'cta_secondary_href', '#cta')},
    }

    # Marquee
    marquee_items = [
        'Machine Learning', 'Deep Learning', 'NLP & LLM', 'Computer Vision',
        'Architecture Cloud', 'APIs & Microservices', 'Python & TensorFlow',
        'R&D en IA', 'Solutions Entreprise', 'MLOps & DevOps','Chat Bot & Agent IA'
    ]

    # About
    about = {
        'eyebrow':    config.about_eyebrow,
        'title':      config.about_title,
        'paragraphs': [p for p in [config.about_para1, config.about_para2] if p],
        'pills': ['Modèles IA sur mesure', 'Architecture logicielle', 'R&D appliquée',
                  'Solutions entreprise', 'Sous-traitance technique', 'Web & Mobile','Chat Bot & Agent IA'],
        'trust_cards': [
            {'icon': '🏢', 'title': 'PME & ETI','desc': 'Automatisation, outils IA intégrés et solutions sur mesure pour les entreprises en croissance.'},
            {'icon': '🌐', 'title': 'Grandes entreprises','desc': "Architecture IA à l'échelle, intégration dans des systèmes complexes et accompagnement stratégique."},
            {'icon': '🤝', 'title': 'Partenaires tech','desc': "Sous-traitance technique, renfort d'équipes et expertise IA pour agences et ESN."},
            {'icon': '🚀', 'title': 'Startups & scale-ups','desc': "Du proof of concept au déploiement production — vitesse d'exécution et excellence technique."},
        ],
    }

    # Solutions
    sq = Solution.objects.filter(is_active=True).order_by('order')
    solutions = {
        'eyebrow': 'Solutions',
        'title':   'Ce que nous construisons pour votre entreprise',
        'items': [{'icon': s.icon, 'title': s.title, 'desc': s.description, 'tag': s.tag, 'featured': s.is_featured} for s in sq]
        or [
            {'icon': '🧠', 'title': 'AryadRH',                   'desc': "Logiciel RH augmenté par l'IA.",            'tag': 'Produit phare →', 'featured': True},
            {'icon': '⚙️', 'title': "Modèles d'IA personnalisés",'desc': 'Modèles sur mesure adaptés à vos données.',  'tag': 'Sur mesure →',    'featured': False},
            {'icon': '🔄', 'title': 'Automatisation intelligente','desc': 'Agents IA et workflows intelligents.',        'tag': 'Process AI →',    'featured': False},
            {'icon': '📱', 'title': 'Applications Web & Mobile', 'desc': 'Fullstack avec capacités IA natives.',        'tag': 'Fullstack AI →',  'featured': False},
            {'icon': '🔬', 'title': 'Conseil & R&D en IA',       'desc': 'Feuille de route IA, POC, transfert.',        'tag': 'Stratégie →',     'featured': False},
            {'icon': '🤝', 'title': 'Sous-traitance technique',  'desc': 'CTO externalisé, lead technique IA.',         'tag': 'Partenariat →',   'featured': False},
        ],
    }

    # Process
    pq = ProcessStep.objects.filter(is_active=True).order_by('order')
    process = {
        'eyebrow':  'Processus',
        'title':    'Comment nous travaillons',
        'subtitle': 'Un processus structuré, de la compréhension du besoin à la mise en production — sans approximation.',
        'steps': [{'num': s.number, 'title': s.title, 'desc': s.description} for s in pq]
        or [
            {'num': '01', 'title': 'Découverte',         'desc': 'Analyse du contexte, objectifs métier et contraintes techniques.'},
            {'num': '02', 'title': 'Architecture',        'desc': 'Conception système, choix technologiques et planification IA.'},
            {'num': '03', 'title': 'Modélisation IA',     'desc': "Développement, entraînement et évaluation des modèles d'IA."},
            {'num': '04', 'title': 'Développement',       'desc': 'Intégration des modèles, interfaces et APIs.'},
            {'num': '05', 'title': 'Déploiement & Scale', 'desc': 'Mise en production cloud, monitoring et optimisation continue.'},
        ],
    }

    # Technologies
    tq = Technology.objects.filter(is_active=True).order_by('order')
    technologies = {
        'eyebrow': 'Stack technique',
        'title':   'Technologies maîtrisées',
        'categories': [
            {'key': 'all',   'label': 'Tout'},
            {'key': 'ai',    'label': 'IA & ML'},
            {'key': 'web',   'label': 'Web & Mobile'},
            {'key': 'cloud', 'label': 'Cloud & DevOps'},
        ],
        'items': [{'icon': t.icon, 'name': t.name, 'cat': t.category} for t in tq]
    }

    # CTA
    cta = {
        'eyebrow':  config.cta_eyebrow,
        'title':    config.cta_title    or "Construisons ensemble des systèmes intelligents qui transforment votre entreprise.",
        'subtitle': config.cta_subtitle or "Vous avez un projet ambitieux à résoudre par l'IA ? Discutons-en.",
        'button':   {'label': config.cta_button_label, 'href': config.cta_button_href},
        'note':     config.cta_note,
    }

    # Chatbot
    chatbot = {
        'greeting':    config.chatbot_greeting,
        'suggestions': config.chatbot_suggestions or [
            'Voir les solutions IA', 'Planifier un appel', 'En savoir plus sur AryadRH',
        ],
    }

    return render(request, 'index.html', {
        'meta':          {'title': 'ARYAD Studio',
                          'description': "ARYAD conçoit et déploie des systèmes d'IA sur mesure."},
        'hero':           hero,
        'marquee_items':  marquee_items,
        'about':          about,
        'solutions':      solutions,
        'process':        process,
        'technologies':   technologies,
        'cta':            cta,
        'chatbot':        chatbot,
        'config':         config,
    })

# ══════════════════════════════════════════════════════════
#  VUE 3 — CHAT
# ══════════════════════════════════════════════════════════

@csrf_exempt
@require_http_methods(['POST'])
def chat_view(request):
    """
    POST /api/chat/

    Body JSON :
    {
      "message":         "Bonjour, je veux en savoir plus",
      "visitor_uid":     "uuid-visiteur",      // optionnel
      "conversation_id": "uuid-conversation"   // optionnel
    }

    Réponse JSON :
    {
      "status":           "ok",
      "reply":            "...",
      "conversation_id":  "uuid",
      "visitor_uid":      "uuid",
      "is_new_conv":      true,
      "response_time_ms": 42
    }
    """
    t0 = time.time()

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'JSON invalide'}, status=400)

    user_message = (data.get('message') or '').strip()
    if not user_message:
        return JsonResponse({'error': 'Message vide'}, status=400)
    if len(user_message) > 500:
        return JsonResponse({'error': 'Message trop long (max 500 caractères)'}, status=400)

    # Visiteur & conversation
    visitor          = _get_or_create_visitor(request, data.get('visitor_uid'))
    conv, mem, is_new = _get_or_create_conversation(visitor, data.get('conversation_id'))

    # Sauvegarder le message utilisateur
    Message.objects.create(conversation=conv, role=Message.Role.USER, content=user_message)
    mem.push('user', user_message)

    # Contexte = 4 derniers messages
    context   = mem.get_context()
    config    = SiteConfig.get()
    bot_reply = _bot_reply(user_message, context, config)

    ms = int((time.time() - t0) * 1000)

    # Sauvegarder la réponse bot
    Message.objects.create(
        conversation=conv, role=Message.Role.BOT,
        content=bot_reply, response_time_ms=ms,
    )
    mem.push('bot', bot_reply)

    return JsonResponse({
        'status':           'ok',
        'reply':            bot_reply,
        'conversation_id':  str(conv.id),
        'visitor_uid':      str(visitor.uid),
        'is_new_conv':      is_new,
        'response_time_ms': ms,
    })

