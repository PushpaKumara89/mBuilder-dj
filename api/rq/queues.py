import django
django.setup()

import itertools
import logging
from time import sleep

from rq import Queue
from rq.compat import as_text
from rq.exceptions import NoSuchJobError
from rq.utils import backend_class


class CommandProjectQueue(Queue):
    @classmethod
    def dequeue_any(cls, queues, timeout, connection=None, job_class=None, serializer=None):
        """Class method returning the job_class instance at the front of the given
        set of Queues, where the order of the queues is important.

        When all of the Queues are empty, depending on the `timeout` argument,
        either blocks execution of this function for the duration of the
        timeout or until new messages arrive on any of the queues, or returns
        None.

        See the documentation of cls.lpop for the interpretation of timeout.
        """
        job_class = backend_class(cls, 'job_class', override=job_class)

        while True:
            queues_list = cls.get_queues_by_regex_name(queues, connection, job_class, serializer)
            queue_keys = [q.key for q in queues_list]
            result = cls.lpop(queue_keys, None, connection=connection)
            if result is None:
                sleep(1)
                continue

            queue_key, job_id = map(as_text, result)
            queue = cls.from_queue_key(queue_key,
                                       connection=connection,
                                       job_class=job_class,
                                       serializer=serializer)
            try:
                job = job_class.fetch(job_id, connection=connection, serializer=serializer)
            except NoSuchJobError:
                # Silently pass on jobs that don't exist (anymore),
                # and continue in the look
                continue
            except Exception as e:
                # Attach queue information on the exception for improved error
                # reporting
                e.job_id = job_id
                e.queue = queue
                raise e
            return job, queue
        return None, None

    @classmethod
    def get_queues_by_regex_name(cls, queues, connection, job_class, serializer):
        logger = logging.getLogger(__name__)
        queues_keys = [
            [
                queue_key.decode('utf-8').replace(queue.redis_queue_namespace_prefix, '')
                for queue_key
                in list(connection.keys(queue.key))
            ]
            for queue in queues
        ]
        queues_keys = list(itertools.chain.from_iterable(queues_keys))
        logger.info('Queues: ' + str(queues_keys))
        # Add 'default' queue as a stump to prevent error for empty queue list.
        queues_keys.append('default')

        sorted(queues_keys)

        return [cls(name=q, connection=connection,
                    job_class=job_class, serializer=serializer)
                for q in queues_keys]
