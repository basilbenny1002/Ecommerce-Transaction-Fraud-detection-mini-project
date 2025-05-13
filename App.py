import flet as ft

# def main(page: ft.Page):
#     page.title = "Flet counter example"
#     page.vertical_alignment = ft.MainAxisAlignment.CENTER

#     txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

#     def minus_click(e):
#         txt_number.value = str(int(txt_number.value) - 1)
#         page.update()

#     def plus_click(e):
#         txt_number.value = str(int(txt_number.value) + 1)
#         page.update()

#     page.add(
#         ft.Row(
#             [
#                 ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
#                 txt_number,
#                 ft.IconButton(ft.Icons.ADD, on_click=plus_click),
#             ],
#             alignment=ft.MainAxisAlignment.CENTER,
#         )
#     )

# ft.app(main)
#TODO SAMPLE GUI
import flet as ft

class App:
    def __init__(self):
        self.page = None
        self.txt_number = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)
        

    def main(self, page: ft.Page):
        self.page = page
        self.page.title = "Windows Media Search"
        self.page.window_width = 500
        self.page.window_height = 400
        self.page.bgcolor = '#a3b9ff'
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        # Create buttons
        minus_btn = ft.ElevatedButton("-", on_click=self.minus_click)
        plus_btn = ft.ElevatedButton("+", on_click=self.plus_click)

        # Add all to page
        self.page.add(
            ft.Row(
                [minus_btn, self.txt_number, plus_btn],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

    def minus_click(self, e):
        self.txt_number.value = str(int(self.txt_number.value) - 1)
        self.page.update()

    def plus_click(self, e):
        self.txt_number.value = str(int(self.txt_number.value) + 1)
        self.page.update()

if __name__ == '__main__':
    app = App()
    ft.app(target=app.main)
