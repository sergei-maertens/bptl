import factory
import factory.fuzzy


class FetchedTaskFactory(factory.django.DjangoModelFactory):
    worker_id = factory.Sequence(lambda n: f"worker-{n}")
    topic_name = factory.fuzzy.FuzzyChoice(["initalize-zaak", "set-zaak-status"])
    task_id = factory.Sequence(lambda n: f"task-{n}")

    class Meta:
        model = "external_tasks.FetchedTask"
