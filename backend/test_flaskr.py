import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Who's the author of the book 'Steve Jobs' published in 2013 and 2015?",
                             "answer": "Walter Isaacson", "difficulty": 3, "category": 4}
        self.previous_questions = [17, 24]

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_show_categories_success(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(data['total_categories'], len(categories))

    def test_show_categories_method_not_allowed(self):
        res = self.client().get('/categories/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource could not be found')

    def test_show_questions_success(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], len(Question.query.all()))
        self.assertEqual(data['current_category'], 'all')
        self.assertEqual(len(data['categories']), len(Category.query.all()))

    def test_show_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Resource could not be found')

    def test_delete_question_success(self):
        res = self.client().delete('/questions/47')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 47).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 47)
        self.assertEqual(question, None)

    def test_delete_question_unprocessable(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_new_question_success(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_new_question_unprocessable(self):
        res = self.client().post('/questions/98', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], 'method not allowed')

    def test_search_question_success(self):
        res = self.client().post('/questions', json={"searchTerm": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], len(
            Question.query.filter(Question.question.ilike('%title%')).all()))
        self.assertEqual(data['current_category'], 'all')

    def test_search_question_without_results(self):
        res = self.client().post(
            '/questions', json={"searchTerm": "applejacks"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)

    def test_questions_by_category_success(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'], len(
            Question.query.filter(Question.category == 1).all()))
        self.assertEqual(data['current_category'], 'Science')

    def test_questions_by_category_unprocessable(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'unprocessable')

    def test_quiz_success(self):
        res = self.client().post('/quizzes',
                                 json={"previous_questions": self.previous_questions, "quiz_category": {"id": 2, "type": "Art"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_quiz_question_unprocessable(self):
        res = self.client().post('/quizzes',
                                 json={"previous_questions": self.previous_questions})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)
        self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
