"""
Quiz views — no database, fully stateless.
All scoring and session state lives in the browser (JavaScript).
"""
import json
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .question_generator import generate_question


def index(request):
    """Serve the main quiz SPA."""
    return render(request, 'quiz/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def api_generate_question(request):
    """
    POST /api/generate-question/
    Body: { "difficulty": "easy|medium|hard", "category": "linear|quadratic|inequality|substitution" }
    Returns a randomly generated algebra question.
    """
    try:
        body = json.loads(request.body)
        difficulty = body.get('difficulty', 'medium')
        category = body.get('category', None)
    except (json.JSONDecodeError, AttributeError):
        difficulty = 'medium'
        category = None

    if difficulty not in ('easy', 'medium', 'hard'):
        difficulty = 'medium'

    question_data = generate_question(difficulty=difficulty, category=category)
    return JsonResponse({'success': True, 'data': question_data})


@csrf_exempt
@require_http_methods(["POST"])
def api_check_answer(request):
    """
    POST /api/check-answer/
    Body: { "user_answer": "...", "correct_answer": "...", "explanation": "..." }
    Returns: { is_correct, correct_answer, explanation }
    """
    try:
        body = json.loads(request.body)
        user_answer = body.get('user_answer', '').strip()
        correct_answer = body.get('correct_answer', '').strip()
        explanation = body.get('explanation', '')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    is_correct = _answers_match(user_answer, correct_answer)
    return JsonResponse({
        'success': True,
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'explanation': explanation,
    })


# ─── Helper ───────────────────────────────────────────────────────────────────

def _normalize(s):
    """Normalize answer string for flexible comparison."""
    s = s.strip().lower()
    s = re.sub(r'\s+', '', s)
    return s


def _answers_match(user_answer, correct_answer):
    """Flexible answer comparison — handles spaces, case, ordering, inequalities."""
    u = _normalize(user_answer)
    c = _normalize(correct_answer)

    if u == c:
        return True

    # Try numeric comparison
    try:
        return float(u) == float(c)
    except ValueError:
        pass

    # Comma-separated roots (quadratic) — order-independent
    if ',' in c:
        c_parts = sorted([_normalize(p) for p in c.split(',')])
        u_parts = sorted([_normalize(p) for p in u.split(',')])
        if c_parts == u_parts:
            return True

    # Inequality: "x > 3" == "x>3"
    u_ineq = re.sub(r'[xX]\s*([><=!≥≤]+)\s*(-?\d+\.?\d*)', r'x\1\2', u)
    c_ineq = re.sub(r'[xX]\s*([><=!≥≤]+)\s*(-?\d+\.?\d*)', r'x\1\2', c)
    if u_ineq == c_ineq:
        return True

    # Simultaneous: "x=2, y=3" == "x=2,y=3"
    if 'x=' in c and 'y=' in c:
        c_parts = sorted([_normalize(p) for p in re.split(r'[,;]', c)])
        u_parts = sorted([_normalize(p) for p in re.split(r'[,;]', u)])
        if c_parts == u_parts:
            return True

    return False
