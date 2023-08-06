#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from uuid import UUID

import logging
from tornado.web import RequestHandler
from tornado import gen
from ujson import dumps
from motorengine import Q

from holmes.models import Review


class BaseReviewHandler(RequestHandler):
    def _parse_uuid(self, uuid):
        try:
            return UUID(uuid)
        except ValueError:
            return None


class ReviewHandler(BaseReviewHandler):
    @gen.coroutine
    def get(self, page_uuid, review_uuid):
        review = None
        if self._parse_uuid(review_uuid):
            review = yield Review.objects.get(uuid=review_uuid)

        if not review:
            self.set_status(404, 'Review with uuid of %s not found!' % review_uuid)
            self.finish()
            return

        yield review.load_references(['page'])
        yield review.page.load_references(['domain'])

        self.write(dumps(review.to_dict()))
        self.finish()


class CompleteReviewHandler(BaseReviewHandler):
    @gen.coroutine
    def post(self, page_uuid, review_uuid):
        review = None
        if self._parse_uuid(review_uuid):
            review = yield Review.objects.get(uuid=review_uuid)

        if not review:
            self.set_status(404, 'Review with uuid of %s not found!' % review_uuid)
            logging.debug('Review with uuid of %s not found!' % review_uuid)
            self.finish()
            return

        if review.is_complete:
            self.set_status(400, 'Review with uuid %s is already completed!' % review_uuid)
            logging.debug('Review with uuid %s is already completed!' % review_uuid)
            self.finish()
            return

        review.is_complete = True
        review.is_active = True
        review.completed_date = datetime.now()

        yield review.load_references(['page'])
        review.page.last_review = review
        review.page.last_review_date = review.completed_date
        yield review.page.save()
        yield review.save()

        self._remove_older_reviews_with_same_day(review)

        query = Q(page=review.page) & Q(uuid__ne=review_uuid)

        yield Review.objects.filter(query).update({
            Review.is_active: False
        })

        self.write('OK')
        self.finish()

    @gen.coroutine
    def _remove_older_reviews_with_same_day(self, review):
        dt = datetime.now()
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        query = Q(page=review.page) & Q(uuid__ne=review.uuid) & Q(created_date__gt=dt)
        yield Review.objects.filter(query).delete()
