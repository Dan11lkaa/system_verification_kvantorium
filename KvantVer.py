import flet as ft
import datetime
import mysql.connector
from mysql.connector import Error
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='t47941022',
    database='Kvantorium_database'
)

try:
    if conn.is_connected():
        cursor = conn.cursor()

        query = "CREATE DATABASE IF NOT EXISTS kvantorium_database"
        cursor.execute(query)
        print("база данных успешно создана или уже существует.")
        cursor.execute("USE kvantorium_database")

        tables = {
            'registration': """
            CREATE TABLE IF NOT EXISTS registration (
            ID BIGINT AUTO_INCREMENT PRIMARY KEY,
            MAIL VARCHAR(100) NOT NULL,
            FUO VARCHAR(100) NOT NULL,
            DATE VARCHAR(40) NOT NULL,
            NAPR VARCHAR(200) NOT NULL,
            PASSWORD VARCHAR(100) NOT NULL
            )"""
        }

        for table_name, query in tables.items():
            cursor.execute(query)
            print(f"Таблица '{table_name}' создана или уже существует.")

        cursor.close()
except Error as e:
    print(f"Ошибка: {e}")

print("Подключено к базе данных Kvantorium_database")

end=None
def main(page: ft.Page):
    page.title = "Kvantorium"
    page.route = page.route
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def kek(e):
        if e.control.selected_index == 0:
            go_to_main(e)
        elif e.control.selected_index == 1:
            go_to_leaderboard(e)
        elif e.control.selected_index == 2:
            go_to_history(e)
        elif e.control.selected_index == 3:
            go_to_faq(e)
        elif e.control.selected_index == 4:
            go_to_login(e)

    def kek_2(e):
        if e.control.selected_index == 0:
            go_to_leaderboard(e)
        elif e.control.selected_index == 1:
            go_to_history(e)
        elif e.control.selected_index == 2:
            go_to_faq(e)
        elif e.control.selected_index == 3:
            go_to_login(e)

    def navigation(param):
        global end
        if param:
            end = page.navigation_bar = ft.NavigationBar(
                on_change=kek,
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.ADMIN_PANEL_SETTINGS, label="Админ панель"),
                    ft.NavigationBarDestination(icon=ft.Icons.DATE_RANGE, label="Лидерборд"),
                    ft.NavigationBarDestination(icon=ft.Icons.HISTORY_OUTLINED, label="История"),
                    ft.NavigationBarDestination(icon=ft.Icons.INFO, label="FAQ"),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.EXIT_TO_APP,
                        selected_icon=ft.Icons.EXIT_TO_APP,
                        label="Выйти",
                    ),
                ]
            )
        else:
            end = page.navigation_bar = ft.NavigationBar(
                on_change=kek_2,
                destinations=[
                    ft.NavigationBarDestination(icon=ft.Icons.DATE_RANGE, label="Лидерборд"),
                    ft.NavigationBarDestination(icon=ft.Icons.HISTORY_OUTLINED, label="История"),
                    ft.NavigationBarDestination(icon=ft.Icons.INFO, label="FAQ"),
                    ft.NavigationBarDestination(
                        icon=ft.Icons.EXIT_TO_APP,
                        selected_icon=ft.Icons.EXIT_TO_APP,
                        label="Выйти",
                    ),
                ]
            )

    def go_to_leaderboard(e):
        page.go('/leaderboard')

    def go_to_login(e):
        show_dialog = ft.Ref()

        def show_logout_dialog():
            dialog = ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Вы действительно хотите выйти с аккаунта?", size=24),
                        ft.Row(
                            [
                                ft.ElevatedButton("Да", on_click=logout, width=150, height=50),
                                ft.ElevatedButton("Нет", on_click=close_dialog, width=150, height=50)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=20,
                border_radius=10,
                border=ft.border.all(2, ft.colors.BLACK),
                visible=True,
                alignment=ft.alignment.center,
                width=400,
                height=250,
                margin=ft.margin.symmetric(horizontal=50)
            )

            page.views.append(dialog)
            page.update()

        def logout(e):
            page.go("/login")

        def close_dialog(e):
            page.views.pop()
            page.update()

        show_logout_dialog()


    def go_to_register(e):
        page.go("/register")

    def go_to_main(e):
        page.go("/main")

    def go_to_history(e):
        page.go("/history")

    def go_to_faq(e):
        page.go('/faq')


    def create_main_page():
        napr_list = []
        students = []
        student_naprs = {}
        checkboxes, grade_fields, comment_fields, date_buttons, action_dropdowns, selected_dates = {}, {}, {}, {}, {}, {}

        cursor = conn.cursor(buffered=True)

        try:
            cursor.execute("SHOW COLUMNS FROM grades LIKE 'napr'")
            column_exists = cursor.fetchone()

            if not column_exists:
                cursor.execute("ALTER TABLE grades ADD COLUMN napr VARCHAR(100)")
                conn.commit()
        except mysql.connector.Error as err:
            if err.errno == 1146:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS grades (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_name VARCHAR(255),
                        grade VARCHAR(10),
                        comment TEXT,
                        date DATE,
                        napr VARCHAR(100)
                    )
                ''')
                conn.commit()

        cursor.execute("SELECT DISTINCT napr FROM registration WHERE napr IS NOT NULL AND napr != ''")
        napr_results = cursor.fetchall()
        for napr in napr_results:
            if napr[0] and napr[0].strip():
                napr_list.append(napr[0])

        def save_data(student, grade, comment, date, napr=None):
            try:
                cursor = conn.cursor(buffered=True)
                cursor.execute("INSERT INTO grades (student_name, grade, comment, date, napr) VALUES (%s, %s, %s, %s, %s)",
                               (student, grade, comment, date, napr))
                conn.commit()
                cursor.close()
                return True
            except Exception as e:
                print(f"Ошибка при сохранении данных: {e}")
                return False

        def delete_data(student, grade, comment, date, napr=None):
            try:
                cursor = conn.cursor(buffered=True)

                query = "DELETE FROM grades WHERE student_name=%s AND grade=%s AND date=%s"
                params = [student, grade, date]

                if comment:
                    query += " AND comment=%s"
                    params.append(comment)

                if napr:
                    query += " AND napr=%s"
                    params.append(napr)

                cursor.execute(query, tuple(params))
                affected_rows = cursor.rowcount
                conn.commit()
                cursor.close()

                return affected_rows
            except Exception as e:
                print(f"Ошибка при удалении данных: {e}")
                return 0

        def update_button_color(student):
            if student in date_buttons:
                date_buttons[student].bgcolor = "green" if selected_dates.get(student) else "red"
                page.update()
            else:
                print(f"Предупреждение: Студент '{student}' не найден в словаре date_buttons")

        def pick_date(e, student):
            print(f"Выбор даты для студента: {student}")

            def set_date(picker_event):
                if picker_event.control.value:
                    print(f"Установка даты для {student}: {picker_event.control.value}")
                    selected_dates[student] = picker_event.control.value.strftime('%Y-%m-%d')
                    update_button_color(student)
                    page.update()

            date_picker = ft.DatePicker(
                first_date=datetime.datetime(2025, 1, 1),
                last_date=datetime.datetime(2025, 12, 31),
                on_change=set_date
            )

            if date_picker not in page.overlay:
                page.overlay.append(date_picker)
                page.update()

            date_picker.open = True
            page.update()

        def autofill_data(e):
            example_student = None
            for student in students:
                if (student in grade_fields and grade_fields[student].value and
                        student in comment_fields and comment_fields[student].value and
                        student in selected_dates and selected_dates.get(student)):
                    example_student = student
                    break

            if example_student:
                example_grade = grade_fields[example_student].value
                example_comment = comment_fields[example_student].value
                example_date = selected_dates[example_student]
                example_action = action_dropdowns[example_student].value

                for target_student in students:
                    if target_student in grade_fields and target_student in comment_fields:
                        grade_fields[target_student].value = example_grade
                        comment_fields[target_student].value = example_comment
                        selected_dates[target_student] = example_date
                        action_dropdowns[target_student].value = example_action
                        checkboxes[target_student].value = True
                        update_button_color(target_student)

                page.open(ft.SnackBar(ft.Text("Данные автоматически заполнены")))
            else:
                page.open(ft.SnackBar(ft.Text("Нет заполненных данных для копирования")))

            page.update()

        def clear_student_fields(student):
            if student in grade_fields:
                grade_fields[student].value = ""
            if student in comment_fields:
                comment_fields[student].value = ""
            if student in selected_dates:
                selected_dates[student] = ""
                update_button_color(student)
            if student in action_dropdowns:
                action_dropdowns[student].value = "Добавить"
            if student in checkboxes:
                checkboxes[student].value = False

        def apply_changes(e, student):
            action = action_dropdowns[student].value
            current_napr = napr_dropdown.value
            if current_napr == "Все направления":
                current_napr = None

            selected_students = []
            for target_student in students:
                if target_student in checkboxes and checkboxes[target_student].value:
                    selected_students.append(target_student)

            for target_student in selected_students:
                grade = grade_fields[target_student].value.strip() if target_student in grade_fields else ""
                comment = comment_fields[target_student].value.strip() if target_student in comment_fields else ""
                date = selected_dates.get(target_student, "")

                student_napr = student_naprs.get(target_student, "Не указано")
                if student_napr == "Не указано":
                    student_napr = None

                if not grade or not date:
                    page.open(ft.SnackBar(ft.Text("Ошибка! Заполнены не все поля")))
                    page.update()
                    continue

                if action == "Добавить":
                    if save_data(target_student, grade, comment, date, student_napr):
                        page.open(ft.SnackBar(ft.Text("Баллы добавлены!")))
                        clear_student_fields(target_student)
                    else:
                        page.open(ft.SnackBar(ft.Text("Ошибка добавления баллов!")))
                elif action == "Удалить":
                    rows_deleted = delete_data(target_student, grade, comment, date, student_napr)
                    if rows_deleted > 0:
                        page.open(ft.SnackBar(ft.Text("Удаление прошло успешно!")))
                        clear_student_fields(target_student)
                    else:
                        page.open(ft.SnackBar(ft.Text("Ошибка! Данной информации нет в базе.")))

                page.update()

        def reset_fields():
            for student in students:
                clear_student_fields(student)
            page.update()
            page.open(ft.SnackBar(ft.Text("Все поля очищены")))

        def load_students_by_napr(e):
            selected_napr = napr_dropdown.value
            print(f"Выбрано направление: {selected_napr}")

            students.clear()
            student_naprs.clear()
            checkboxes.clear()
            grade_fields.clear()
            comment_fields.clear()
            date_buttons.clear()
            action_dropdowns.clear()
            selected_dates.clear()

            cursor = conn.cursor(buffered=True)
            if selected_napr == "Все направления":
                cursor.execute("SELECT fuo, napr FROM registration WHERE fuo IS NOT NULL AND fuo != ''")
                print("Загружаем всех студентов")
            else:
                cursor.execute("SELECT fuo, napr FROM registration WHERE napr=%s AND fuo IS NOT NULL AND fuo != ''", (selected_napr,))
                print(f"Загружаем студентов по направлению: {selected_napr}")

            student_results = cursor.fetchall()
            print(f"Найдено студентов: {len(student_results)}")
            cursor.close()

            for student_row in student_results:
                student_name = student_row[0]
                student_napr = student_row[1] if len(student_row) > 1 else "Не указано"
                if student_name and student_name.strip():
                    students.append(student_name)
                    student_naprs[student_name] = student_napr

            for student in students:
                checkboxes[student] = ft.Checkbox()
                grade_fields[student] = ft.TextField(width=80, hint_text="Баллы")
                comment_fields[student] = ft.TextField(width=300, hint_text="Комментарий")

                date_buttons[student] = ft.ElevatedButton(
                    "Дата",
                    bgcolor="red",
                    width=80,
                    on_click=lambda e, s=student: pick_date(e, s)
                )

                action_dropdowns[student] = ft.Dropdown(
                    options=[
                        ft.dropdown.Option("Добавить"),
                        ft.dropdown.Option("Удалить")
                    ],
                    value="Добавить",
                    width=120
                )
                selected_dates[student] = ""

            create_student_table()

        def create_student_table():
            for i, control in enumerate(main_content.controls):
                if hasattr(control, '_is_student_table'):
                    main_content.controls.pop(i)
                    break

            control_row = ft.Row([
                ft.ElevatedButton("Автозаполнение", on_click=autofill_data),
                ft.ElevatedButton("Очистить всё", on_click=lambda e: reset_fields()),
            ], alignment=ft.MainAxisAlignment.CENTER)

            control_TEXT = ft.Row([
                ft.Text(f"Всего найдено учеников: {len(students)}")], alignment=ft.MainAxisAlignment.CENTER)

            header_row = ft.Row([
                ft.Text("Выбрать", width=70),
                ft.Text("Студент", width=150),
                ft.Text("Направление", width=150),
                ft.Text("Баллы", width=80),
                ft.Text("Комментарий", width=300),
                ft.Text("Дата", width=80),
                ft.Text("Действие", width=120),
                ft.Text("Применить", width=65)
            ], alignment=ft.MainAxisAlignment.START)

            student_table = ft.Column([
                control_TEXT,
                control_row,
                ft.Divider(),
                header_row,
                ft.Divider()
            ])
            student_table._is_student_table = True

            if not students:
                student_table.controls.append(ft.Text("Нет учеников для выбранного направления",
                                                      style=ft.TextStyle(italic=True)))
            else:
                student_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=400)

                for student in students:
                    apply_button = ft.FloatingActionButton(
                        icon=ft.icons.CHECK,
                        height=45,
                        width=65,
                        on_click=lambda e, s=student: apply_changes(e, s)
                    )

                    student_list.controls.append(
                        ft.Row([
                            checkboxes[student],
                            ft.Text(student, width=150, tooltip=student),
                            ft.Text(student_naprs.get(student, "Не указано"), width=150, tooltip=student_naprs.get(student, "Не указано")),
                            grade_fields[student],
                            comment_fields[student],
                            date_buttons[student],
                            action_dropdowns[student],
                            apply_button
                        ])
                    )

                student_table.controls.append(student_list)

            main_content.controls.append(student_table)
            page.update()

        napr_dropdown = ft.Dropdown(
            label="Выберите направление",
            options=[ft.dropdown.Option("Все направления")] + [ft.dropdown.Option(napr) for napr in napr_list],
            width=300,
            value="Все направления",
            on_change=load_students_by_napr
        )

        main_content = ft.Column([])
        global end
        main_view = ft.View(
            route="/main",
            controls=[
                ft.AppBar(title=ft.Text("Админ панель"), bgcolor=ft.colors.BLUE_500, center_title=True),
                end,
                ft.Row([napr_dropdown], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                main_content
            ],
        )

        page.on_load = lambda _: load_students_by_napr(None)

        load_students_by_napr(None)

        return main_view

    def create_leaderboard_page():
        def mysql1():
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    g.student_name, 
                    r.MAIL, 
                    r.DATE,
                    r.NAPR,
                    SUM(g.grade) AS total_score
                FROM grades g
                JOIN registration r ON g.student_name = r.FUO
                GROUP BY g.student_name, r.MAIL, r.DATE, r.NAPR;
            """)

            fef = cursor.fetchall()
            cursor.close()

            sorted_data = sorted([list(row) for row in fef], key=lambda x: x[4], reverse=True)

            for i, row in enumerate(sorted_data):
                row.insert(0, i + 1)

            return sorted_data

        def table1(rows):
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Место")),
                    ft.DataColumn(ft.Text("ФИО")),
                    ft.DataColumn(ft.Text("Почта")),
                    ft.DataColumn(ft.Text("Дата рождения")),
                    ft.DataColumn(ft.Text("Направление")),
                    ft.DataColumn(ft.Text("Общий балл")),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(rank))),
                            ft.DataCell(ft.Text(full_name)),
                            ft.DataCell(ft.Text(email)),
                            ft.DataCell(ft.Text(birth_date)),
                            ft.DataCell(ft.Text(course)),
                            ft.DataCell(ft.Text(str(score)))
                        ]
                    )
                    for rank, full_name, email, birth_date, course, score in rows
                ]
            )

        def main1():
            data = mysql1()
            filtered_data = data.copy()
            current_page = 0
            users_per_page = 10

            search_options = ["Все", "ФИО", "Почта", "Дата рождения", "Направление", "Общий балл"]
            search_field = ft.TextField(label="Поиск", on_change=lambda e: update_table(0), width=400)
            search_dropdown = ft.Dropdown(
                label="Выбрать столбец",
                width=400,
                options=[ft.dropdown.Option(option) for option in search_options],
                value="Все",
                on_change=lambda e: update_table(0)
            )

            prev_button = ft.ElevatedButton("Назад", on_click=lambda e: change_page(-1))
            next_button = ft.ElevatedButton("Вперёд", on_click=lambda e: change_page(1))
            page_indicator = ft.Text()
            table_container = ft.Container(content=table1(filtered_data[:users_per_page]))

            def update_table(new_page):
                nonlocal filtered_data, current_page
                query = search_field.value.lower()
                column_index = search_options.index(search_dropdown.value)

                if not query:
                    filtered_data = data.copy()
                else:
                    if column_index == 0:
                        filtered_data = [row for row in data if query in " ".join(map(str, row[1:])).lower()]
                    else:
                        filtered_data = [row for row in data if query in str(row[column_index]).lower()]

                current_page = new_page
                update_pagination()

            def change_page(direction):
                nonlocal current_page
                new_page = current_page + direction
                if 0 <= new_page < (len(filtered_data) // users_per_page) + 1:
                    current_page = new_page
                    update_pagination()

            def update_pagination():
                start = current_page * users_per_page
                end = start + users_per_page
                visible_data = filtered_data[start:end]

                total_pages = max(1, (len(filtered_data) // users_per_page) + 1)
                page_indicator.value = f"Страница {current_page + 1} из {total_pages}"

                prev_button.disabled = current_page == 0
                next_button.disabled = end >= len(filtered_data)

                table_container.content = table1(visible_data)
                page.update()

            total_pages = max(1, (len(filtered_data) // users_per_page) + 1)
            page_indicator.value = f"Страница 1 из {total_pages}"

            return [
                search_dropdown,
                search_field,
                ft.Row([prev_button, page_indicator, next_button], alignment=ft.MainAxisAlignment.CENTER),
                table_container
            ]

        return ft.View(
            route="/leaderboard",
            controls=[
                ft.AppBar(title=ft.Text("Лидерборд"), bgcolor=ft.colors.BLUE_500, center_title=True),
                end,
                *main1()
            ]
        )

    def create_history_page():
        def mysql1():
            cursor = conn.cursor()
            cursor.execute("SELECT student_name, grade, comment, date, napr FROM grades ORDER BY date DESC")
            fef = cursor.fetchall()
            cursor.close()
            return [list(row) for row in fef]

        def table1(rows):
            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Ученик")),
                    ft.DataColumn(ft.Text("Оценка")),
                    ft.DataColumn(ft.Text("Комментарий")),
                    ft.DataColumn(ft.Text("Дата")),
                    ft.DataColumn(ft.Text("Направление"))
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(student)),
                            ft.DataCell(ft.Text(str(grade))),
                            ft.DataCell(ft.Text(comment)),
                            ft.DataCell(ft.Text(str(date))),
                            ft.DataCell(ft.Text(napr))
                        ]
                    )
                    for student, grade, comment, date, napr in rows
                ]
            )

        def main1():
            data = mysql1()
            filtered_data = data.copy()
            current_page = 0
            users_per_page = 10

            search_options = ["Все", "Ученик", "Оценка", "Комментарий", "Дата", "Направление"]
            search_field = ft.TextField(label="Поиск", on_change=lambda e: update_table(0), width=400)
            search_dropdown = ft.Dropdown(
                label="Выбрать столбец",
                width=400,
                options=[ft.dropdown.Option(option) for option in search_options],
                value="Все",
                on_change=lambda e: update_table(0)
            )

            prev_button = ft.ElevatedButton("Назад", on_click=lambda e: change_page(-1))
            next_button = ft.ElevatedButton("Вперёд", on_click=lambda e: change_page(1))
            page_indicator = ft.Text()
            table_container = ft.Container(content=table1(filtered_data[:users_per_page]))

            refresh_button = ft.ElevatedButton("Сбросить", on_click=lambda e: refresh_data())

            def update_table(new_page):
                nonlocal filtered_data, current_page
                query = search_field.value.lower()
                column_index = search_options.index(search_dropdown.value)

                if not query:
                    filtered_data = data.copy()
                else:
                    if column_index == 0:
                        filtered_data = [row for row in data if query in " ".join(map(str, row)).lower()]
                    else:
                        adjusted_index = column_index - 1
                        filtered_data = [row for row in data if query in str(row[adjusted_index]).lower()]

                current_page = new_page
                update_pagination()

            def change_page(direction):
                nonlocal current_page
                new_page = current_page + direction
                if 0 <= new_page < (len(filtered_data) // users_per_page) + 1:
                    current_page = new_page
                    update_pagination()

            def update_pagination():
                start = current_page * users_per_page
                end = start + users_per_page
                visible_data = filtered_data[start:end]

                total_pages = max(1, (len(filtered_data) // users_per_page) + 1)
                page_indicator.value = f"Страница {current_page + 1} из {total_pages}"

                prev_button.disabled = current_page == 0
                next_button.disabled = end >= len(filtered_data)

                table_container.content = table1(visible_data)
                page.update()

            def refresh_data():
                nonlocal data, filtered_data, current_page
                data = mysql1()
                filtered_data = data.copy()
                current_page = 0
                update_pagination()
                search_field.value = ''
                page.open(ft.SnackBar(ft.Text("Поиск сброшен!")))
                page.update()

            total_pages = max(1, (len(filtered_data) // users_per_page) + 1)
            page_indicator.value = f"Страница 1 из {total_pages}"

            return [search_dropdown, search_field, refresh_button,
                ft.Row([prev_button, page_indicator, next_button], alignment=ft.MainAxisAlignment.CENTER),
                table_container
            ]

        return ft.View(
            route="/history",
            controls=[
                ft.AppBar(title=ft.Text("История выставления баллов"), bgcolor=ft.colors.BLUE_500, center_title=True),
                end,
                *main1()
            ]
        )


    def create_faq_page():
        return ft.View(
            route="/faq",
            controls=[
                ft.AppBar(title=ft.Text("FAQ"), bgcolor=ft.colors.BLUE_500, center_title=True),
                end,
                ft.Text('Тут будет инструкция использования приложения, а также критерии выставления баллов участникам и контакты тех-поддержки .', size=24)
                    ]
                )


    def create_register_page(e):
        go_to_register(e)
        num = None
        def register(mail, fuo, date, napr, password, num):
            page.views.clear()
            def check(e):
                if numbers.value == num:
                    print(f"Введен правильный код: {numbers.value}")
                    cursor = conn.cursor()

                    check_query = "SELECT * FROM registration WHERE MAIL = %s"
                    cursor.execute(check_query, (mail.value,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        page.open(ft.SnackBar(ft.Text("Пользователь с таким email уже зарегистрирован!")))
                        print(f"Пользователь с email {mail.value} уже существует.")
                    else:
                        query = """
                            INSERT INTO registration (MAIL, FUO, DATE, NAPR, PASSWORD) 
                            VALUES (%s, %s, %s, %s, %s)
                            """
                        values = (mail.value, fuo.value, date.value, napr.value, password.value)
                        try:
                            cursor.execute(query, values)
                            conn.commit()
                            page.open(ft.SnackBar(ft.Text("Вы успешно зарегистрировались!")))
                            print("Данные успешно добавлены в базу данных.")
                            go_to_login(e)
                        except Error as e:
                            page.open(ft.SnackBar(ft.Text(f"Ошибка при добавлении в базу данных: {e}")))
                            print(f"Ошибка: {e}")
                    cursor.close()
                else:
                    page.open(ft.SnackBar(ft.Text("Неверный код подтверждения!")))
                    print(f"Неверный код: {numbers.value}. Ожидаемый код: {num}")
                page.update()

            numbers = ft.TextField(label='Код подтверждения', width=230)
            but = ft.OutlinedButton(text='Зарегистрироваться', on_click=check, disabled=True)

            def enable_button(e):
                but.disabled = numbers.value == ""
                page.update()

            numbers.on_change = enable_button

            page.views.append(
                ft.View(
                route='/register',
                controls=[
                    ft.AppBar(title=ft.Text("Регистрация"), bgcolor=ft.colors.BLUE_500, center_title=True),
                    ft.Text('На указанный gmail пришел 4-значный код подтверждения. Введи его:'),
                    numbers,
                    but
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
            page.update()


        def prov(e, mail, fuo, date, napr, password, password_2, bin_register):
            if all([mail.value, fuo.value, date.value, napr.value, password.value, password_2.value]):
                bin_register.disabled = False
            else:
                bin_register.disabled = True
            page.update()

        def send_code(e, mail, fuo, date, napr, password, password_2):
            nonlocal num
            if password.value == password_2.value:
                num = str(random.randint(1000, 9999))
                print(f"Сгенерированный код: {num}")
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                sender_email = 'kvantorium27@gmail.com'
                sender_password = "ykow zuzh fnpn fjgd"
                receiver_email = mail.value

                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = receiver_email
                msg["Subject"] = "Код доступа в приложение учета кванторианцев"
                body = f"Ваш код для регистрации: {num}"
                msg.attach(MIMEText(body, "plain"))

                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, msg.as_string())
                    print("Письмо отправлено успешно!")
                except Exception as ex:
                    print("Ошибка:", ex)
                finally:
                    server.quit()
                register(mail, fuo, date, napr, password, num)
            else:
                page.open(ft.SnackBar(ft.Text("Пароли не совпадают!")))
                password.value = ''
                password_2.value = ''
                page.update()

        mail = ft.TextField(label='Почта', width=400, on_change=lambda e: prov(e, mail, fuo, date, napr, password, password_2, bin_register))
        fuo = ft.TextField(label='ФИО', width=400, on_change=lambda e: prov(e, mail, fuo, date, napr, password, password_2, bin_register))
        date = ft.TextField(label='Дата рождения. Формат DD-MM-YYYY', width=400, on_change=lambda e: prov(e, mail, fuo, date, napr, password, password_2, bin_register))
        napr = ft.Dropdown(
            label="Направление в кванториуме",
            width=400,
            on_change=lambda e: prov(e, mail, fuo, date, napr, password, password_2, bin_register),
            options=[
                ft.dropdown.Option("Электроника"),
                ft.dropdown.Option("Программирование на Python (1 группа)"),
                ft.dropdown.Option("VR/AR"),
                ft.dropdown.Option("Программирование на Python (2 группа)"),
            ]
        )
        password = ft.TextField(label='Пароль', width=400, on_change=lambda e: prov(e, mail, fuo, date, napr, password, password_2, bin_register), password=True)
        password_2 = ft.TextField(label='Подтвердите пароль', width=400, on_change=lambda e: prov(e, mail, fuo, date, napr, password, password_2, bin_register), password=True)

        bin_register = ft.FilledButton(text='Получить код подтверждения', on_click=lambda e: send_code(e, mail, fuo, date, napr, password, password_2), disabled=True)

        return ft.View(
            route="/login",
            controls=[
                ft.AppBar(title=ft.Text("Регистрация"), bgcolor=ft.colors.BLUE_500, center_title=True),
                ft.Container(
                    content=ft.Column(
                        [
                            mail,
                            fuo,
                            date,
                            napr,
                            password,
                            password_2,
                            bin_register
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    alignment=ft.alignment.center,
                ),
            ],
        )


    def create_login_page():
        def validate(e):
            if all([user_login.value, user_pass.value]):
                bin_reg.disabled = False
            else:
                bin_reg.disabled = True
            page.update()

        user_login = ft.TextField(label="Почта", on_change=validate, width=500, height=70)
        user_pass = ft.TextField(label='Пароль', on_change=validate, width=500, height=70, password=True)

        def reg(e):
            cursor = conn.cursor()

            try:
                query = "SELECT * FROM registration WHERE MAIL = %s AND PASSWORD = %s"
                cursor.execute(query, (user_login.value, user_pass.value))

                user = cursor.fetchone()

                if user:
                    page.open(ft.SnackBar(ft.Text("Вы успешно авторизовались как ученик!")))
                    navigation(param=False)
                    go_to_leaderboard(e)
                elif user_login.value == 'admin' and user_pass.value == 'k13v69an27t':
                    navigation(param=True)
                    go_to_main(e)
                    page.open(ft.SnackBar(ft.Text("Вы успешно авторизовались как администратор!")))
                else:
                    page.open(ft.SnackBar(ft.Text("Неверный логин или пароль!")))

            except mysql.connector.Error as err:
                page.open(ft.SnackBar(ft.Text(f"Ошибка при запросе: {err}")))
            finally:
                cursor.close()
        bin_reg = ft.CupertinoButton(text='Войти', on_click=reg, disabled=True, height=50, width=250, bgcolor=ft.colors.BLUE_500, color='white')
        bin_email = ft.OutlinedButton(text='Регистрация', on_click=create_register_page)
        return ft.View(
            route="/login",
            controls=[
                ft.AppBar(title=ft.Text("Авторизация"), bgcolor=ft.colors.BLUE_500, center_title=True),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=10),
                            ft.Text('Система учета кванторианцев', color=ft.colors.BLUE_500, size=30),
                            ft.Container(height=20),
                            user_login,
                            user_pass,
                            bin_reg,
                            bin_email
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    alignment=ft.alignment.center,
                ),
            ],
        )


    def route_change(e):
        page.views.clear()
        page.views.append(
            create_login_page() if page.route == "/login" or page.route == "/"
            else create_register_page(e) if page.route == "/register"
            else create_main_page() if page.route == "/main"
            else create_leaderboard_page() if page.route == "/leaderboard"
            else create_faq_page() if page.route == "/faq"
            else create_history_page() if page.route == "/history"
            else ft.View(route=page.route, controls=[ft.Text("404! Not Found")])
        )
        page.update()

    page.on_route_change = route_change
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
