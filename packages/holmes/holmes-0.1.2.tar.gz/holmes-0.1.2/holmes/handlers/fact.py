#!/usr/bin/python
# -*- coding: utf-8 -*-

from uuid import UUID

from tornado.web import RequestHandler
from tornado import gen

from holmes.models import Review


class CreateFactHandler(RequestHandler):

    @gen.coroutine
    def post(self, page_uuid, review_uuid):
        key = self.get_argument('key')
        unit = self.get_argument('unit', None)
        value = self.get_argument('value')

        parsed_uuid = None
        try:
            parsed_uuid = UUID(review_uuid)
        except ValueError:
            pass

        review = None
        if parsed_uuid:
            review = yield Review.objects.get(uuid=parsed_uuid)

        if not review:
            self.set_status(404, 'Review with uuid of %s not found!' % review_uuid)
            self.finish()
            return

        review.add_fact(key=key, unit=unit, value=value)
        yield review.save()

        self.write('OK')
        self.finish()
