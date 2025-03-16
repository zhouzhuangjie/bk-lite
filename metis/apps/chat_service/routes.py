from apps.chat_service.runnable.openai_runnable import OpenAIRunnable


def register_routes(app):
    OpenAIRunnable().register(app)
