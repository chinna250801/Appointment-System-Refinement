import reflex as rx
import os


class Config(rx.Config):
    pass


config = Config(app_name="app", plugins=[rx.plugins.TailwindV3Plugin()])
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")