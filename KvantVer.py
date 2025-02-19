import flet as ft
import datetime

def main(page: ft.Page):
    page.title = "Kvantorium"
    page.route = page.route
    page.vertical_alignment = ft.MainAxisAlignment.CENTER


    def go_to_login(e):
        page.go("/login")

    def go_to_register(e):
        page.go("/register")

    def go_to_main(e):
        page.go("/main")

    def go_to_top(e):
        page.go("/top")


    def create_main_page():
        return ft.View(
            route="/main",
            controls=[
                ft.AppBar(title=ft.Text("Главная"), bgcolor=ft.colors.GREEN_600),
                ft.ElevatedButton("Главная", on_click=lambda _: page.go("/main"), autofocus=True),
                ft.ElevatedButton("Расписание", on_click=lambda _: page.go("/calendar")),
                ft.ElevatedButton("Направления", on_click=lambda _: page.go("/directions")),
                ft.ElevatedButton("Баллы", on_click=lambda _: page.go("/top")),
            ],
        )


    def create_calendar_page():
        return ft.View(
            route="/calendar",
            controls=[
                ft.AppBar(title=ft.Text("Расписание"), bgcolor=ft.colors.GREEN_600),
                ft.ElevatedButton("Главная", on_click=lambda _: page.go("/main")),
                ft.ElevatedButton("Расписание", on_click=lambda _: page.go("/calendar"), autofocus=True),
                ft.ElevatedButton("Направления", on_click=lambda _: page.go("/directions")),
                ft.ElevatedButton("Баллы", on_click=lambda _: page.go("/top")),
            ],
        )


    def create_directions_page():
        return ft.View(
            route="/directions",
            controls=[
                ft.AppBar(title=ft.Text("Направления"), bgcolor=ft.colors.GREEN_600),
                ft.ElevatedButton("Главная", on_click=lambda _: page.go("/main")),
                ft.ElevatedButton("Расписание", on_click=lambda _: page.go("/calendar")),
                ft.ElevatedButton("Направления", on_click=lambda _: page.go("/directions"), autofocus=True),
                ft.ElevatedButton("Баллы", on_click=lambda _: page.go("/top")),
            ],
        )

    def create_top_page():
        return ft.View(
            route="/top",
            controls=[
                ft.AppBar(title=ft.Text("Баллы"), bgcolor=ft.colors.GREEN_600),
                ft.ElevatedButton("Главная", on_click=lambda _: page.go("/main")),
                ft.ElevatedButton("Расписание", on_click=lambda _: page.go("/calendar")),
                ft.ElevatedButton("Направления", on_click=lambda _: page.go("/directions")),
                ft.ElevatedButton("Баллы", on_click=lambda _: page.go("/top"), autofocus=True),
            ],
        )


    def create_register_page():
        fio_field = ft.TextField(label="ФИО",autofocus=True)
        email_field = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL)
        birthdate_field = ft.TextField(label="Дата рождения (ДД.ММ.ГГГГ)")
        password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
        confirm_password_field = ft.TextField(label="Повторите пароль", password=True, can_reveal_password=True)
        error_message = ft.Text("", color=ft.colors.RED)

        def register_click(e):

            if not all([fio_field.value, email_field.value, birthdate_field.value, password_field.value, confirm_password_field.value]):
                 error_message.value = "Пожалуйста, заполните все поля."
                 page.update()
                 return

            if password_field.value != confirm_password_field.value:
                error_message.value = "Пароли не совпадают."
                page.update()
                return

            print("Регистрация прошла успешно")
            page.go("/login")

        register_button = ft.ElevatedButton("Зарегистрироваться", on_click=register_click)
        login_link = ft.TextButton("Уже есть аккаунт? Войти", on_click=go_to_login)

        return ft.View(
            route="/register",
            controls=[
                ft.AppBar(title=ft.Text("Регистрация"), bgcolor=ft.colors.BLUE_GREY_400),
                ft.Column(
                    [
                        fio_field,
                        email_field,
                        birthdate_field,
                        password_field,
                        confirm_password_field,
                        register_button,
                        login_link,
                        error_message,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
        )


    def create_login_page():
        login_field = ft.TextField(label="Логин",autofocus=True)
        password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
        error_message = ft.Text("", color=ft.colors.RED)
        register_link = ft.TextButton("Еще не зарегистрированы?", on_click=go_to_register)

        def login_click(e):
            if login_field.value == "adm" and password_field.value == "adm":
                page.go("/main")
            else:
                error_message.value = "Неверный логин или пароль"
                page.update()

        login_button = ft.ElevatedButton("Войти", on_click=login_click)

        return ft.View(
            route="/login",
            controls=[
                ft.AppBar(title=ft.Text("Вход"), bgcolor=ft.colors.BLUE_GREY_400),
                ft.Column(
                    [
                        login_field,
                        password_field,
                        login_button,
                        register_link,
                        error_message,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
        )


    def route_change(e):
        page.views.clear()
        page.views.append(
            create_login_page() if page.route == "/login" or page.route == "/"
            else create_register_page() if page.route == "/register"
            else create_main_page() if page.route == "/main"
            else create_calendar_page() if page.route == "/calendar"
            else create_directions_page() if page.route == "/directions"
            else create_top_page() if page.route == "/top"
            else ft.View(route=page.route, controls=[ft.Text("404! Not Found")])
        )
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)
