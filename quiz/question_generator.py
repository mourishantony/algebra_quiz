"""
Algebra question generator for multiple categories and difficulty levels.
Generates questions dynamically using Python math logic.
"""
import random
import math


def generate_question(difficulty='medium', category=None):
    """
    Generate a random algebra question based on difficulty and category.
    Returns a dict: { question, answer, hint, explanation, category, difficulty }
    """
    generators = {
        'easy': [
            _one_step_linear,
            _simple_substitution,
            _basic_inequality,
        ],
        'medium': [
            _two_step_linear,
            _distributive_law,
            _simultaneous_simple,
        ],
        'hard': [
            _quadratic_factorable,
            _hard_inequality,
            _simultaneous_hard,
        ],
    }

    category_map = {
        'linear': {
            'easy': _one_step_linear,
            'medium': _two_step_linear,
            'hard': _simultaneous_hard,
        },
        'quadratic': {
            'easy': _quadratic_factorable,
            'medium': _quadratic_factorable,
            'hard': _quadratic_factorable,
        },
        'inequality': {
            'easy': _basic_inequality,
            'medium': _hard_inequality,
            'hard': _hard_inequality,
        },
        'substitution': {
            'easy': _simple_substitution,
            'medium': _distributive_law,
            'hard': _simultaneous_hard,
        },
    }

    if category and category in category_map:
        gen_fn = category_map[category].get(difficulty, category_map[category]['medium'])
    else:
        fns = generators.get(difficulty, generators['medium'])
        gen_fn = random.choice(fns)

    return gen_fn()


# ─── EASY ────────────────────────────────────────────────────────────────────

def _one_step_linear():
    """ax = b  or  x + a = b"""
    style = random.choice(['multiply', 'add', 'subtract'])
    if style == 'multiply':
        a = random.randint(2, 12)
        x = random.randint(1, 15)
        b = a * x
        question = f"Solve for x: &nbsp;<strong>{a}x = {b}</strong>"
        explanation = f"Divide both sides by {a}: x = {b} ÷ {a} = <strong>{x}</strong>"
        hint = f"Divide both sides by {a}"
    elif style == 'add':
        a = random.randint(1, 20)
        x = random.randint(1, 20)
        b = x + a
        question = f"Solve for x: &nbsp;<strong>x + {a} = {b}</strong>"
        explanation = f"Subtract {a} from both sides: x = {b} − {a} = <strong>{x}</strong>"
        hint = f"Subtract {a} from both sides"
    else:
        a = random.randint(1, 20)
        x = random.randint(1, 20)
        b = x - a
        question = f"Solve for x: &nbsp;<strong>x − {a} = {b}</strong>"
        explanation = f"Add {a} to both sides: x = {b} + {a} = <strong>{x}</strong>"
        hint = f"Add {a} to both sides"
    return {
        'question': question,
        'answer': str(x),
        'hint': hint,
        'explanation': explanation,
        'category': 'Linear (1-step)',
        'difficulty': 'easy',
    }


def _simple_substitution():
    """Given y = expr, find y when x = value"""
    a = random.randint(1, 8)
    b = random.randint(0, 10)
    x_val = random.randint(1, 10)
    y_val = a * x_val + b
    question = (f"If &nbsp;<strong>y = {a}x + {b}</strong>, "
                f"what is <strong>y</strong> when <strong>x = {x_val}</strong>?")
    explanation = (f"Substitute x = {x_val}: &nbsp;"
                   f"y = {a}×{x_val} + {b} = {a*x_val} + {b} = <strong>{y_val}</strong>")
    hint = f"Substitute x = {x_val} into the equation"
    return {
        'question': question,
        'answer': str(y_val),
        'hint': hint,
        'explanation': explanation,
        'category': 'Substitution',
        'difficulty': 'easy',
    }


def _basic_inequality():
    """Simple one-step inequality: x + a > b"""
    ops = [('>', '<'), ('<', '>'), ('≥', '≤'), ('≤', '≥')]
    op, rev_op = random.choice(ops)
    a = random.randint(1, 15)
    x = random.randint(1, 20)
    b = x + a
    question = f"Solve for x: &nbsp;<strong>x + {a} {op} {b}</strong>"
    explanation = (f"Subtract {a} from both sides: "
                   f"x {op} {b} − {a} = <strong>x {op} {x}</strong>")
    hint = f"Subtract {a} from both sides"
    return {
        'question': question,
        'answer': f"x {op} {x}",
        'hint': hint,
        'explanation': explanation,
        'category': 'Inequality',
        'difficulty': 'easy',
    }


# ─── MEDIUM ──────────────────────────────────────────────────────────────────

def _two_step_linear():
    """ax + b = c"""
    a = random.randint(2, 8)
    x = random.randint(-10, 10)
    b = random.randint(-15, 15)
    c = a * x + b
    b_str = f"+ {b}" if b >= 0 else f"− {abs(b)}"
    c_display = c
    question = f"Solve for x: &nbsp;<strong>{a}x {b_str} = {c_display}</strong>"
    explanation = (
        f"Step 1 — Move constant: {a}x = {c} − ({b}) = {c - b}<br>"
        f"Step 2 — Divide by {a}: x = {c - b} ÷ {a} = <strong>{x}</strong>"
    )
    hint = f"First subtract {b} from both sides, then divide by {a}"
    return {
        'question': question,
        'answer': str(x),
        'hint': hint,
        'explanation': explanation,
        'category': 'Linear (2-step)',
        'difficulty': 'medium',
    }


def _distributive_law():
    """a(x + b) = c"""
    a = random.randint(2, 6)
    b = random.randint(1, 10)
    x = random.randint(-8, 8)
    c = a * (x + b)
    question = f"Solve for x: &nbsp;<strong>{a}(x + {b}) = {c}</strong>"
    explanation = (
        f"Step 1 — Expand: {a}x + {a*b} = {c}<br>"
        f"Step 2 — Subtract {a*b}: {a}x = {c - a*b}<br>"
        f"Step 3 — Divide by {a}: x = <strong>{x}</strong>"
    )
    hint = f"First expand: {a}×x + {a}×{b} = {c}"
    return {
        'question': question,
        'answer': str(x),
        'hint': hint,
        'explanation': explanation,
        'category': 'Distributive',
        'difficulty': 'medium',
    }


def _simultaneous_simple():
    """Simple simultaneous: x + y = a, x - y = b"""
    x = random.randint(1, 10)
    y = random.randint(1, 10)
    a = x + y
    b = x - y
    b_str = str(b) if b >= 0 else str(b)
    question = (f"Solve the simultaneous equations:<br>"
                f"<strong>x + y = {a}</strong><br>"
                f"<strong>x − y = {b_str}</strong><br>"
                f"Find the value of <strong>x</strong>.")
    explanation = (
        f"Add both equations: 2x = {a} + ({b_str}) = {a+b}<br>"
        f"Divide by 2: x = <strong>{x}</strong>"
    )
    hint = "Try adding both equations together to eliminate y"
    return {
        'question': question,
        'answer': str(x),
        'hint': hint,
        'explanation': explanation,
        'category': 'Simultaneous',
        'difficulty': 'medium',
    }


# ─── HARD ────────────────────────────────────────────────────────────────────

def _quadratic_factorable():
    """(x + p)(x + q) = 0 → x² + (p+q)x + pq = 0"""
    p = random.randint(-8, 8)
    q = random.randint(-8, 8)
    while q == p:
        q = random.randint(-8, 8)
    b = p + q
    c = p * q
    b_str = f"+ {b}x" if b > 0 else (f"− {abs(b)}x" if b < 0 else "")
    c_str = f"+ {c}" if c > 0 else (f"− {abs(c)}" if c < 0 else "")
    question = f"Solve for x: &nbsp;<strong>x² {b_str} {c_str} = 0</strong>"
    r1, r2 = -p, -q
    if r1 > r2:
        r1, r2 = r2, r1
    answer_str = f"{r1}, {r2}" if r1 != r2 else str(r1)
    explanation = (
        f"Factor: (x + {p})(x + {q}) = 0<br>"
        f"So x + {p} = 0 → x = {-p}<br>"
        f"Or x + {q} = 0 → x = {-q}<br>"
        f"Solutions: x = <strong>{answer_str}</strong>"
    )
    hint = f"Find two numbers that multiply to {c} and add to {b}"
    return {
        'question': question,
        'answer': answer_str,
        'hint': hint,
        'explanation': explanation,
        'category': 'Quadratic',
        'difficulty': 'hard',
    }


def _hard_inequality():
    """ax + b > cx + d"""
    a = random.randint(2, 8)
    c = random.randint(1, a - 1)
    x = random.randint(-5, 10)
    b = random.randint(-10, 10)
    d = (a - c) * x + b - random.randint(1, 5)
    lhs = f"{a}x + {b}" if b >= 0 else f"{a}x − {abs(b)}"
    rhs = f"{c}x + {d}" if d >= 0 else f"{c}x − {abs(d)}"
    diff_a = a - c
    diff_d = d - b
    ans_num = d - b
    ans_den = a - c
    ans = ans_num / ans_den
    # find integer answer for clean problem
    real_x = (d - b) / (a - c)
    import math as _math
    threshold = _math.ceil(real_x) if (a - c) > 0 else _math.floor(real_x)
    question = f"Solve for x: &nbsp;<strong>{lhs} &gt; {rhs}</strong>"
    explanation = (
        f"Move x terms left: ({a} − {c})x &gt; {d} − ({b})<br>"
        f"Simplify: {diff_a}x &gt; {d - b}<br>"
        f"Divide by {diff_a}: x &gt; {d - b}/{diff_a} = <strong>{round(real_x, 2)}</strong>"
    )
    answer_str = f"x > {round(real_x, 2)}"
    hint = f"Move all x terms to one side and constants to the other"
    return {
        'question': question,
        'answer': answer_str,
        'hint': hint,
        'explanation': explanation,
        'category': 'Inequality',
        'difficulty': 'hard',
    }


def _simultaneous_hard():
    """2x + 3y = a, 3x - y = b — elimination method"""
    x = random.randint(1, 8)
    y = random.randint(1, 8)
    a = 2 * x + 3 * y
    b = 3 * x - y
    question = (
        f"Solve simultaneously:<br>"
        f"<strong>2x + 3y = {a}</strong><br>"
        f"<strong>3x − y = {b}</strong><br>"
        f"Find <strong>x</strong> and <strong>y</strong>."
    )
    explanation = (
        f"From equation 2: y = 3x − {b}<br>"
        f"Substitute into eq 1: 2x + 3(3x − {b}) = {a}<br>"
        f"→ 2x + 9x − {3*b} = {a}<br>"
        f"→ 11x = {a + 3*b}<br>"
        f"→ x = {x}, y = {y}"
    )
    answer_str = f"x={x}, y={y}"
    hint = "Try substitution: isolate y from equation 2 and substitute into equation 1"
    return {
        'question': question,
        'answer': answer_str,
        'hint': hint,
        'explanation': explanation,
        'category': 'Simultaneous',
        'difficulty': 'hard',
    }
