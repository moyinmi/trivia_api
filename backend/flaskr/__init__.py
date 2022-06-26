
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from collections.abc import Mapping

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    #cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, PUT, POST, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_all_categories(): #get all the categories
        data = Category.query.all()
        categories = {}
        for cat in data:
            categories[cat.id] = cat.type

        if len(data) == 0:
            abort(404)

        return jsonify({
        'success': True,
        'categories': categories
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
    def get_questions(): # get all questions and paginate
        select = Question.query.all() 
        total_quests = len(select) #get total number of questions
        current_quests = paginate_questions(request, select)

        # get all categories
        categories = Category.query.all()
        categories_dict = {}
        for cat in categories:
            categories_dict[cat.id] = cat.type

        
        if (len(current_quests) == 0):
            abort(404)

        # return data to view
        return jsonify({
            'success': True,
            'questions': current_quests,
            'total_questions': total_quests,
            'categories': categories_dict
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['GET','DELETE'])
    def delete_question(id):
        #delete the question with specified question id

        try:
            question = Question.query.get(id)

            if question is None:
                abort(404)

            question.delete()
        
            return jsonify({
            'success': True,
            'deleted': id
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
    @app.route('/questions', methods=['POST'])
    def createQuestion():

        body = request.get_json()

        newQuestion = body['question']
        newAnswer = body['answer']
        newCategory = body['category']
        insert_difficulty = body['difficulty']

        if (len(newQuestion)==0) or (len(newAnswer)==0) or (len(newAnswer)==0) or (len(newAnswer)==0):
            abort(422)

        question = Question(
        question = newQuestion,
        answer = newAnswer,
        category=newCategory,
        difficulty=insert_difficulty
        )

        question.insert()
    
        all_questions = Question.query.all()
        current_questions = paginate_questions(request, all_questions)

        return jsonify({
        'success': True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(all_questions)
        })

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/search", methods=['POST'])
    def search():
        body = request.get_json()
        search = body.get('searchTerm')
        questions = Question.query.filter(
            Question.question.ilike('%'+search+'%')).all()

        if questions:
            currentQuestions = paginate_questions(request, questions)
            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questions)
            })
        else:
            abort(404)



    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions")
    def questions_in_category(id):
       
        category = Category.query.filter_by(id=id).one_or_none()  # gets the category by given id
        if category: # gets all questions in a category
            
            questionsInCat = Question.query.filter_by(category=str(id)).all()
            currentQuestions = paginate_questions(request, questionsInCat)

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questionsInCat),
                'current_category': category.type
            })
        
        else:
            abort(404)

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
    
    def playQuiz():

        body = request.get_json()
        quizCat = body.get('quiz_category')
        previousQuestion = body.get('previous_questions')

        try:
            if (quizCat['id'] == 0):
                questionsQuery = Question.query.all()
            else:
                questionsQuery = Question.query.filter_by(
                    cat=quizCat['id']).all()

            randomId = random.randint(0, len(questionsQuery)-1)
            nextQuestion = questionsQuery[randomId]

            stillQuestions = True
            while nextQuestion.id not in previousQuestion:
                nextQuestion = questionsQuery[randomId]
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": nextQuestion.answer,
                        "category": nextQuestion.cat,
                        "difficulty": nextQuestion.difficulty,
                        "id": nextQuestion.id,
                        "question": nextQuestion.question
                    },
                    'previousQuestion': previousQuestion
                })

        except Exception as e:
            print(e)
            abort(404)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
  
    def bad_request(error):
        return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found. Input out of range.'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        'success': False,
        'error': 422, 
        'message': 'unprocessable. Synax error.'
        }), 422

    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
        'success': False,
        'error': 500, 
        'message': 'Sorry, the falut is us not you. Please try again later.'
        }), 500


    return app

