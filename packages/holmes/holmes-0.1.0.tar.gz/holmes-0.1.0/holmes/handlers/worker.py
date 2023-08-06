#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from tornado import gen
from uuid import UUID
from ujson import dumps

from holmes.models.worker import Worker
from holmes.handlers import BaseHandler


class WorkerHandler(BaseHandler):

    @gen.coroutine
    def post(self, uuid):
        worker_uuid = UUID(uuid)

        worker = yield Worker.objects.get(uuid=worker_uuid)

        if worker:
            worker.last_ping = datetime.now()
            yield worker.save()
        else:
            yield Worker.objects.create(uuid=worker_uuid)

        dt = datetime.now() - timedelta(seconds=self.application.config.ZOMBIE_WORKER_TIME)
        yield Worker.objects.filter(last_ping__lt=dt).delete()

        self.write(str(worker_uuid))
        self.finish()


class WorkersHandler(BaseHandler):

    @gen.coroutine
    def get(self):
        workers = yield Worker.objects.find_all()

        workers_json = []
        for worker in workers:
            worker_dict = worker.to_dict()

            if worker.working:
                yield worker.current_review.load_references(['page'])
                page = worker.current_review.page
                if page:
                    worker_dict['page_url'] = page.url
                    worker_dict['page_uuid'] = str(page.uuid)
            workers_json.append(worker_dict)

        self.write(dumps(workers_json))
        self.finish()
