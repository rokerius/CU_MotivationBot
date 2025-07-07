from .db_posts import PostsDatabase
from .db_pictures import PicturesDatabase
from .db_users import UsersDatabase
from .db_questions import QuestionsDatabase

class Database(PostsDatabase, PicturesDatabase, UsersDatabase, QuestionsDatabase):
    pass

db = Database()
