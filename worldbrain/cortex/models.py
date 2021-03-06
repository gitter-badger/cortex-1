from django.db import models
from django_fsm import FSMField, transition
from django_fsm_log.models import StateLog
from enum import Enum

class SourceStates(Enum):
    PENDING = 'pending'
    CRAWLED = 'crawled'
    REJECTED = 'rejected'
    FAILED = 'failed'

class AllUrlStates(Enum):
    PENDING = 'pending'
    PROCESSED = 'processed'

class ArticleStates(Enum):
    PENDING = 'pending'
    PARSED = 'parsed'
    EXTRACTED = 'extracted'


class Source(models.Model):
    domain_name = models.URLField()
    state = FSMField(default=SourceStates.PENDING.value, db_index=True)

    @transition(
        field=state,
        source='*',
        target=SourceStates.CRAWLED.value
    )
    def crawl(self):
        pass

    @transition(
        field=state,
        source='*',
        target=SourceStates.REJECTED.value
    )
    def reject(self):
        pass

    @transition(
        field=state,
        source=(SourceStates.CRAWLED.value),
        target=SourceStates.FAILED.value,
        custom=dict(admin=False)
    )
    def fail(self):
        pass

    def __str__(self):
            return 'Source [domain_name: {}] [state: {}]'.format(
                self.domain_name, self.state
            )


class AllUrl(models.Model):
    source = models.ForeignKey(
        Source,
        related_name='urls',
        related_query_name='url',
        on_delete=models.CASCADE
    )
    url = models.URLField()
    state = FSMField(default=AllUrlStates.PENDING.value, db_index=True)
    is_article = models.BooleanField(default=True)

    @transition(
        field=state,
        source='*',
        target=AllUrlStates.PROCESSED.value
    )
    def processed(self):
        pass

class Article(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=255)
    domain_name = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    summary = models.CharField(max_length=255)
    links = models.CharField(max_length=255)
    parse_time = models.CharField(max_length=255)
    html = models.TextField()
    publish_date = models.DateField()
    state = FSMField(default=ArticleStates.PENDING.value, db_index=True)

    @transition(
        field=state,
        source='*',
        target=ArticleStates.EXTRACTED.value
    )
    def extracted(self):
        pass

    @transition(
        field=state,
        source='*',
        target=ArticleStates.PARSED.value
    )
    def parsed(self):
        pass

