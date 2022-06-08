import json
import os
from sre_parse import CATEGORIES
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, PUT, POST, DELETE, OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def show_categories():
        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type
        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def show_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        try:
            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]
            current_questions = formatted_questions[start:end]

            if len(current_questions) == 0:
                abort(404)

            categories = {}
            for category in Category.query.all():
                categories[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(formatted_questions),
                'categories': categories,
                'current_category': 'all'
            })
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)
        search = body.get('searchTerm', None)

        try:
            if search:
                questions = Question.query.filter(
                    Question.question.ilike(f'%{search}%')).all()
                formatted_questions = [question.format()
                                       for question in questions]
                return jsonify({
                    'success': True,
                    'questions': formatted_questions,
                    'total_questions': len(formatted_questions),
                    'current_category': 'all'
                })
            else:
                question = Question(
                    question=question, answer=answer, difficulty=difficulty, category=category)
                question.insert()
                return jsonify({
                    'success': True,
                    'created': question.id
                })
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions')
    def get_question_by_category(category_id):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        try:
            questions = Question.query.filter(
                Question.category == category_id).all()
            formatted_questions = [question.format() for question in questions]
            current_questions = formatted_questions[start:end]

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(formatted_questions),
                'current_category': Category.query.filter_by(id=category_id).one_or_none().type
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        try:
            questions = None
            question = None
            if quiz_category['id'] == 0:
                questions = Question.query.filter(
                    ~Question.id.in_(previous_questions)).all()
            else:
                questions = Question.query.filter(Question.category == quiz_category['id']).filter(
                    ~Question.id.in_(previous_questions)).all()
            if len(questions) != 0:
                formatted_questions = [question.format()
                                       for question in questions]
                question = random.choice(formatted_questions)
            return jsonify({
                'success': True,
                'question': question
            })
        except:
            abort(404)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource could not be found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(405)
    def wrong_approach(error):
        return jsonify({
            "success": False, "error": 405, "message": "method not allowed"
        }), 405

    return app
