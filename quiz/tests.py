"""Tests for the no-database version of the Algebra Quiz."""
from django.test import TestCase, Client
from django.urls import reverse
import json

from .question_generator import generate_question
from .views import _answers_match


class QuestionGeneratorTests(TestCase):
    """Tests for the dynamic question generator."""

    def test_easy_question_returns_required_fields(self):
        q = generate_question(difficulty='easy')
        for field in ['question', 'answer', 'hint', 'explanation', 'category', 'difficulty']:
            self.assertIn(field, q, f"Missing field: {field}")

    def test_medium_question_is_generated(self):
        q = generate_question(difficulty='medium')
        self.assertIsInstance(q['answer'], str)
        self.assertTrue(len(q['question']) > 0)

    def test_hard_question_is_generated(self):
        q = generate_question(difficulty='hard')
        self.assertIn(q['difficulty'], ('easy', 'medium', 'hard'))

    def test_category_filter_works(self):
        q = generate_question(difficulty='easy', category='substitution')
        self.assertIn('Substitution', q['category'])

    def test_multiple_generations_are_different(self):
        questions = [generate_question('medium')['question'] for _ in range(10)]
        self.assertGreater(len(set(questions)), 1)


class AnswerMatchingTests(TestCase):
    """Tests for flexible answer comparison."""

    def test_exact_match(self):
        self.assertTrue(_answers_match('5', '5'))

    def test_case_insensitive(self):
        self.assertTrue(_answers_match('X=3', 'x=3'))

    def test_float_equivalence(self):
        self.assertTrue(_answers_match('3.0', '3'))

    def test_quadratic_roots_order_independent(self):
        self.assertTrue(_answers_match('3, -2', '-2, 3'))
        self.assertTrue(_answers_match('-2,3', '3,-2'))

    def test_inequality_with_spaces(self):
        self.assertTrue(_answers_match('x > 3', 'x>3'))

    def test_simultaneous_answer(self):
        self.assertTrue(_answers_match('x=2, y=3', 'x=2,y=3'))

    def test_wrong_answer(self):
        self.assertFalse(_answers_match('4', '5'))


class APITests(TestCase):
    """Integration tests for the stateless REST API."""

    def setUp(self):
        self.client = Client()

    def test_index_returns_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_generate_question_endpoint(self):
        response = self.client.post(
            reverse('api_generate_question'),
            data=json.dumps({'difficulty': 'easy'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('question', data['data'])

    def test_generate_question_medium(self):
        response = self.client.post(
            reverse('api_generate_question'),
            data=json.dumps({'difficulty': 'medium'}),
            content_type='application/json',
        )
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_generate_question_hard(self):
        response = self.client.post(
            reverse('api_generate_question'),
            data=json.dumps({'difficulty': 'hard'}),
            content_type='application/json',
        )
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_check_answer_correct(self):
        response = self.client.post(
            reverse('api_check_answer'),
            data=json.dumps({
                'user_answer': '5',
                'correct_answer': '5',
                'explanation': 'Test explanation',
            }),
            content_type='application/json',
        )
        data = json.loads(response.content)
        self.assertTrue(data['is_correct'])

    def test_check_answer_wrong(self):
        response = self.client.post(
            reverse('api_check_answer'),
            data=json.dumps({
                'user_answer': '99',
                'correct_answer': '5',
                'explanation': 'Test explanation',
            }),
            content_type='application/json',
        )
        data = json.loads(response.content)
        self.assertFalse(data['is_correct'])

    def test_check_answer_with_category_filter(self):
        response = self.client.post(
            reverse('api_generate_question'),
            data=json.dumps({'difficulty': 'easy', 'category': 'linear'}),
            content_type='application/json',
        )
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('answer', data['data'])
