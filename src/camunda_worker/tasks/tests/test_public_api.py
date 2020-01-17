from django.test import TestCase, tag
from django.utils import timezone

from camunda_worker.external_tasks.tests.factories import FetchedTaskFactory

from ..api import NoCallback, TaskExpired, execute
from ..registry import TaskRegistry
from .factories import TaskMappingFactory

register = TaskRegistry()


@register
def task_1(task):
    task.result_variables = {"task_run": "task_1"}
    task.save()


@register
def task_2(task):
    task.result_variables = {"task_run": "task_2"}
    task.save()


@tag("public-api")
class RouteTaskTests(TestCase):
    def test_route_to_correct_task(self):
        # set up the routing decisions
        TaskMappingFactory.create(
            topic_name="task-1", callback=register.get_for(task_1)
        )
        TaskMappingFactory.create(
            topic_name="task-2", callback=register.get_for(task_2)
        )
        # set up fetched tasks
        task1 = FetchedTaskFactory.create(topic_name="task-1")
        task2 = FetchedTaskFactory.create(topic_name="task-2")

        execute(task1, registry=register)
        execute(task2, registry=register)

        task1.refresh_from_db()
        task2.refresh_from_db()

        self.assertEqual(task1.result_variables, {"task_run": "task_1"})
        self.assertEqual(task2.result_variables, {"task_run": "task_2"})

    def test_no_mapping_configured(self):
        task = FetchedTaskFactory.create(topic_name="task-1")

        with self.assertRaises(NoCallback):
            execute(task, registry=register)

    def test_mapping_configured_invalid_callback(self):
        TaskMappingFactory.create(topic_name="task-1", callback="foo.bar")
        task = FetchedTaskFactory.create(topic_name="task-1")

        with self.assertRaises(NoCallback):
            execute(task, registry=register)

    def test_expired_task(self):
        TaskMappingFactory.create(
            topic_name="task-1", callback=register.get_for(task_1)
        )
        task1 = FetchedTaskFactory.create(
            topic_name="task-1", lock_expires_at=timezone.now()
        )

        with self.assertRaises(TaskExpired):
            execute(task1, registry=register)
