from django.db import models

from .workflow import EditorialQuerySet


class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()


class MediaQuerySet(models.QuerySet):
    def images(self):
        return self.filter(media_type='image')

class MediaManager(models.Manager):
    def get_queryset(self):
        return MediaQuerySet(self.model, using=self._db)

    def images(self):
        return self.get_queryset().images()


class ArticleQuerySet(EditorialQuerySet):
    def published(self):
        return self.filter(is_published=True)

    def by_author(self, author):
        return self.filter(author=author)


class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def by_author(self, author):
        return self.get_queryset().by_author(author)

    def due(self, now=None):
        return self.get_queryset().due(now)

    def in_status(self, status):
        return self.get_queryset().in_status(status)




class MagazineQuerySet(EditorialQuerySet):
    def published(self):
        return self.filter(is_published=True)

class MagazineManager(models.Manager):
    def get_queryset(self):
        return MagazineQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def due(self, now=None):
        return self.get_queryset().due(now)

    def in_status(self, status):
        return self.get_queryset().in_status(status)

