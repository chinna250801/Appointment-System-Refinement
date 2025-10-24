import reflex as rx


class Config(rx.Config):
    pass


config = Config(app_name="app", plugins=[rx.plugins.TailwindV3Plugin()])
API_URL = "/api"