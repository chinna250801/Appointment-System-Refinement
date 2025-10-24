import reflex as rx
from app.auth import AuthState


def landing_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Welcome to the Appointment System",
                class_name="text-4xl font-bold text-gray-800",
            ),
            rx.el.p(
                "Your health, simplified.", class_name="text-lg text-gray-600 mt-2"
            ),
            class_name="text-center mb-12",
        ),
        rx.el.div(
            rx.el.a(
                rx.el.div(
                    rx.icon(
                        "user-round",
                        class_name="h-12 w-12 mx-auto mb-4 text-violet-600",
                    ),
                    rx.el.h2(
                        "Patient Portal",
                        class_name="text-xl font-semibold text-gray-700",
                    ),
                    rx.el.p(
                        "Book and manage your appointments.",
                        class_name="text-sm text-gray-500 mt-1",
                    ),
                    class_name="w-full text-center p-8 rounded-2xl shadow-sm border border-gray-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 bg-white",
                ),
                href="/patient/login",
            ),
            rx.el.a(
                rx.el.div(
                    rx.icon(
                        "clipboard-list",
                        class_name="h-12 w-12 mx-auto mb-4 text-gray-700",
                    ),
                    rx.el.h2(
                        "Staff Portal", class_name="text-xl font-semibold text-gray-700"
                    ),
                    rx.el.p(
                        "Access for Doctors and Admins.",
                        class_name="text-sm text-gray-500 mt-1",
                    ),
                    class_name="w-full text-center p-8 rounded-2xl shadow-sm border border-gray-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 bg-white",
                ),
                href="/staff/login",
            ),
            class_name="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto",
        ),
        class_name="flex flex-col items-center justify-center min-h-screen bg-gray-50 font-['Montserrat'] p-8",
    )


def _auth_form(
    title: str,
    submit_text: str,
    handler: rx.event.EventHandler,
    fields: list[dict],
    footer: rx.Component,
) -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.icon("activity", class_name="h-8 w-8 text-violet-600"),
                rx.el.h2(title, class_name="text-2xl font-bold text-gray-800 mt-4"),
                class_name="text-center",
            ),
            rx.el.form(
                rx.foreach(
                    fields,
                    lambda field: rx.el.div(
                        rx.el.label(
                            field["label"],
                            class_name="text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            name=field["name"],
                            type=field["type"],
                            placeholder=field["placeholder"],
                            required=True,
                            class_name="mt-1 w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition",
                        ),
                        class_name="mb-4",
                    ),
                ),
                rx.el.button(
                    submit_text,
                    type="submit",
                    class_name="w-full bg-violet-600 text-white font-semibold p-3 rounded-lg hover:bg-violet-700 transition-all duration-300 shadow-md hover:shadow-lg",
                ),
                on_submit=handler,
                class_name="mt-8",
            ),
            footer,
            class_name="w-full max-w-md bg-white p-8 md:p-10 rounded-2xl shadow-xl border border-gray-100",
        ),
        class_name="min-h-screen flex items-center justify-center bg-gray-100 font-['Montserrat'] p-4",
    )


def staff_login_page() -> rx.Component:
    return _auth_form(
        title="Staff Login",
        submit_text="Login",
        handler=AuthState.staff_login,
        fields=[
            {
                "label": "Username",
                "name": "username",
                "type": "text",
                "placeholder": "Enter your username",
            },
            {
                "label": "Password",
                "name": "password",
                "type": "password",
                "placeholder": "Enter your password",
            },
        ],
        footer=rx.el.p(
            "Login here to manage appointments and administrative tasks.",
            class_name="text-center text-xs text-gray-500 mt-6",
        ),
    )


def patient_login_page() -> rx.Component:
    return _auth_form(
        title="Patient Login",
        submit_text="Login",
        handler=AuthState.patient_login,
        fields=[
            {
                "label": "Username",
                "name": "username",
                "type": "text",
                "placeholder": "Enter your username",
            },
            {
                "label": "Password",
                "name": "password",
                "type": "password",
                "placeholder": "Enter your password",
            },
        ],
        footer=rx.el.div(
            rx.el.p(
                "Don't have an account? ",
                rx.el.a(
                    "Register here",
                    href="/patient/register",
                    class_name="font-semibold text-violet-600 hover:underline",
                ),
                class_name="text-center text-sm text-gray-600 mt-6",
            )
        ),
    )


def patient_register_page() -> rx.Component:
    return _auth_form(
        title="Patient Registration",
        submit_text="Create Account",
        handler=AuthState.patient_register,
        fields=[
            {
                "label": "Username",
                "name": "username",
                "type": "text",
                "placeholder": "Choose a username",
            },
            {
                "label": "Email Address",
                "name": "email",
                "type": "email",
                "placeholder": "your@email.com",
            },
            {
                "label": "Phone Number (Optional)",
                "name": "phone",
                "type": "tel",
                "placeholder": "+1234567890",
            },
            {
                "label": "Password",
                "name": "password",
                "type": "password",
                "placeholder": "Create a strong password",
            },
        ],
        footer=rx.el.div(
            rx.el.p(
                "Already have an account? ",
                rx.el.a(
                    "Login here",
                    href="/patient/login",
                    class_name="font-semibold text-violet-600 hover:underline",
                ),
                class_name="text-center text-sm text-gray-600 mt-6",
            )
        ),
    )


from app.components.admin_sidebar import admin_sidebar


def admin_dashboard_layout(page_content: rx.Component) -> rx.Component:
    return rx.el.div(
        admin_sidebar(),
        rx.el.main(
            page_content,
            class_name="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-6 bg-gray-50",
        ),
        class_name="flex min-h-screen w-full font-['Montserrat']",
    )


def admin_dashboard_page() -> rx.Component:
    content = rx.el.div(
        rx.el.h1("Admin Dashboard", class_name="text-3xl font-bold text-gray-800"),
        rx.el.p(
            "Welcome to the admin dashboard. Here you can manage the system.",
            class_name="text-gray-600 mt-2",
        ),
        class_name="p-6",
    )
    return admin_dashboard_layout(content)


def admin_departments_page() -> rx.Component:
    content = rx.el.h1("Department Management")
    return admin_dashboard_layout(content)


def admin_doctors_page() -> rx.Component:
    content = rx.el.h1("Doctor Management")
    return admin_dashboard_layout(content)


def admin_patients_page() -> rx.Component:
    content = rx.el.h1("Patient Management")
    return admin_dashboard_layout(content)


def admin_appointments_page() -> rx.Component:
    content = rx.el.h1("Appointment Management")
    return admin_dashboard_layout(content)


def placeholder_dashboard(title: str) -> rx.Component:
    return rx.el.div(
        rx.el.h1(f"{title} Dashboard", class_name="text-3xl font-bold text-gray-800"),
        rx.el.p(
            "This is a placeholder for your dashboard content.",
            class_name="text-gray-600 mt-2",
        ),
        rx.el.button(
            "Logout",
            on_click=AuthState.logout,
            class_name="mt-8 bg-violet-500 text-white px-4 py-2 rounded-lg",
        ),
        class_name="flex flex-col items-center justify-center min-h-screen bg-gray-50 font-['Montserrat']",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(landing_page, route="/", on_load=AuthState.check_auth)
app.add_page(staff_login_page, route="/staff/login")
app.add_page(patient_login_page, route="/patient/login")
app.add_page(patient_register_page, route="/patient/register")
app.add_page(
    admin_dashboard_page, route="/admin/dashboard", on_load=AuthState.check_auth
)
app.add_page(
    admin_departments_page, route="/admin/departments", on_load=AuthState.check_auth
)
app.add_page(admin_doctors_page, route="/admin/doctors", on_load=AuthState.check_auth)
app.add_page(admin_patients_page, route="/admin/patients", on_load=AuthState.check_auth)
app.add_page(
    admin_appointments_page, route="/admin/appointments", on_load=AuthState.check_auth
)
app.add_page(
    lambda: placeholder_dashboard("Doctor"),
    route="/doctor/dashboard",
    on_load=AuthState.check_auth,
)
app.add_page(
    lambda: placeholder_dashboard("Patient"),
    route="/patient/dashboard",
    on_load=AuthState.check_auth,
)