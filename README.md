import flet as ft

def main(page: ft.Page):
    page.title = "Страница входа"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    login_field = ft.TextField(label="Логин")
    password_field = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
    error_message = ft.Text("", color=ft.colors.RED)

    def login_click(e):
        if login_field.value == "admin" and password_field.value == "adminKvant25":
            page.go("/main_page")
        else:
            error_message.value = "Неверный логин или пароль"
            page.update()

    login_button = ft.ElevatedButton("Войти", on_click=login_click)

    def view_main_page():
        page.views.append(
            ft.View(
                "/main_page",
                [
                    ft.AppBar(title=ft.Text("Главная страница"), bgcolor=ft.colors.GREEN_900),
                    ft.ElevatedButton(
                        "Главная",
                        on_click=lambda _: page.go("/main_page"),
                    ),
                    ft.ElevatedButton(
                        "Календарь",
                        on_click=lambda _: page.go("/calendar"),
                    ),
                    ft.ElevatedButton(
                        "Направления",
                        on_click=lambda _: page.go("/directions"),
                    ),
                ],
            )
        )
        page.update()

    def view_calendar():
        page.views.append(
            ft.View(
                "/calendar",
                [
                    ft.AppBar(title=ft.Text("Календарь"), bgcolor=ft.colors.BLACK),
                    ft.ElevatedButton(
                        "Вернуться на главную страницу",
                        on_click=lambda _: page.go("/main_page"),
                    ),
                ],
            )
        )
        page.update()

    def view_directions():
        page.views.append(
            ft.View(
                "/directions",
                [
                    ft.AppBar(title=ft.Text("Направления"), bgcolor=ft.colors.GREEN_600),
                    ft.ElevatedButton(
                        "Вернуться на главную страницу",
                        on_click=lambda _: page.go("/main_page"),
                    ),
                ],
            )
        )
        page.update()


    def route_change(e):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Text("Страница входа", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                    login_field,
                    password_field,
                    login_button,
                    error_message,
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                padding=200,
            )
        )
        if page.route == "/main_page":
            view_main_page()
        if page.route == "/calendar":
            view_calendar()
        if page.route == "/directions":
            view_directions()
        page.update()


    page.on_route_change = route_change
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)
