# app/layout.py
from nicegui import ui, app

def header_and_sidebar():
    with ui.header().classes("bg-primary text-white justify-between items-center"):
        ui.label("LearnSphere").classes("text-h6")
        
        user_name = app.storage.user.get("name", "Guest")
        with ui.row().classes("items-center gap-2"):
            ui.label(f"Welcome, {user_name}")
            if app.storage.user.get("authenticated"):
                def logout():
                    app.storage.user.clear()
                    ui.navigate.to("/login")
                ui.button("Log out", on_click=logout).props("flat color=white")

    with ui.left_drawer().classes("bg-slate-100"):
        ui.label("Navigation").classes("text-subtitle1 font-bold q-mb-md")
        role = app.storage.user.get("role", "")
        if role:
            ui.link("Dashboard", f"/{role}")
            ui.link("Classes", "/classes")