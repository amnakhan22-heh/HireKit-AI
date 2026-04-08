import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class GeneratorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "generator"

    def ready(self):
        from .rag import initialize_knowledge_base

        try:
            initialize_knowledge_base()
        except Exception as error:
            logger.warning(
                "RAG knowledge base initialization failed: %s. "
                "Requests will proceed without RAG context until this is resolved.",
                error,
            )
