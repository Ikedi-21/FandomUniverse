import re
from django.urls import reverse
from catalog.models import Category
from .models import ChatbotFAQ

FALLBACK = ("I'm not sure about that one. Try asking about searching, bookmarks, "
            "events or submitting fan content, or use the feedback form.")
MIN_SCORE = 2


def _clean(text):
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', text.lower())).strip()


def _score(faq, clean):
    padded, words, score = f' {clean} ', set(clean.split()), 0
    for kw in faq.keyword_list():
        kw = _clean(kw)
        if not kw:
            continue
        if f' {kw} ' in padded:                       # whole phrase matched
            score += len(kw.split()) * 2
        else:                                          # partial: individual words
            score += sum(1 for w in kw.split() if len(w) > 2 and w in words)
    return score


def detect_category(clean):
    padded = f' {clean} '
    for cat in Category.objects.all():
        name = _clean(cat.name)                        # "K-Pop" -> "k pop"
        if f' {name} ' in padded or f' {name.replace(" ", "")} ' in padded:
            return cat
    return None


def _explore_chip(category):
    # change 'catalog:explore' and ?category= to match your explorer's URL name and filter param
    return {'label': f'Browse {category.name} →',
            'href': f"{reverse('catalog:explore')}?category={category.slug}"}


def get_response(message):
    clean = _clean(message)
    mentioned = detect_category(clean)

    best, best_score = None, 0
    for faq in ChatbotFAQ.objects.filter(is_active=True).select_related('category'):
        s = _score(faq, clean)
        if s > best_score:
            best, best_score = faq, s

    if best and best_score >= MIN_SCORE:
        answer = best.answer
        category = mentioned or best.category          # use the FAQ's own category if none was typed
    elif mentioned:
        best = None
        answer = f"Looking for {mentioned.name}? You can browse everything in that category on the explorer."
        category = mentioned
    else:
        return {'answer': FALLBACK, 'chips': [], 'faq': None}

    chips = [_explore_chip(category)] if category else []
    return {'answer': answer, 'chips': chips, 'faq': best}