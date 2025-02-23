from .models import Category, Article, Media, Magazine
from .utils import validate_article_data

class CategoryService:
    @staticmethod
    def create_category(name, description=''):
        return Category.create_category(name, description)

    @staticmethod
    def get_all_categories():
        return Category.get_all_categories()

    @staticmethod
    def update_category(category_id, name=None, description=None):
        return Category.update_category(category_id, name, description)

    @staticmethod
    def delete_category(category_id):
        return Category.delete_category(category_id)

class ArticleService:
    @staticmethod
    def create_article(title, content, author, categories=None, tags=None):
        validate_article_data(title, content)
        return Article.create_article(title, content, author, categories, tags)

    @staticmethod
    def get_all_articles():
        return Article.get_all_articles()

    @staticmethod
    def update_article(article_id, title=None, content=None):
        return Article.update_article(article_id, title, content)

    @staticmethod
    def delete_article(article_id):
        return Article.delete_article(article_id)

class MediaService:
    @staticmethod
    def upload_media(file, media_type, alt_text=''):
        return Media.upload_media(file, media_type, alt_text)

    @staticmethod
    def get_all_media():
        return Media.get_all_media()

class MagazineService:
    @staticmethod
    def create_magazine(title, description='', cover_image=None):
        return Magazine.create_magazine(title, description, cover_image)

    @staticmethod
    def get_all_magazines():
        return Magazine.get_all_magazines()

    @staticmethod
    def update_magazine(magazine_id, title=None, description=None):
        return Magazine.update_magazine(magazine_id, title, description)

    @staticmethod
    def delete_magazine(magazine_id):
        return Magazine.delete_magazine(magazine_id)
