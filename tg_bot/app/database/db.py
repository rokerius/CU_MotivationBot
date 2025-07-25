from .db_posts import PostsDatabase
from .db_pictures import PicturesDatabase
from .db_users import UsersDatabase
from .db_questions import QuestionsDatabase
from .db_quizzes import QuizzesDatabase
from .db_utils import UtilsDatabase


class Database(PostsDatabase, PicturesDatabase, UsersDatabase,
               QuestionsDatabase, QuizzesDatabase, UtilsDatabase):
    pass

db = Database()
