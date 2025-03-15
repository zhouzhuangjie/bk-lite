from langserve import add_routes

from apps.example.runnable.example_runnable import ExampleRunnable


def register_routes(app):
    ExampleRunnable().register(app)
