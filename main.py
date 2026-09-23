import ast
import math
import operator

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView


# ============================================================
# SAFE MATH ENGINE
# ============================================================

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calculate_expression(expression):
    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = expression.replace("−", "-")
    expression = expression.replace("^", "**")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):

        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError

        if isinstance(node, ast.BinOp):

            operation = OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError

            left = evaluate(node.left)
            right = evaluate(node.right)

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):

            operation = UNARY_OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError

            return operation(evaluate(node.operand))

        raise ValueError

    result = evaluate(tree)

    if not math.isfinite(result):
        raise ValueError

    return result


def format_number(value):

    if isinstance(value, float):

        if value.is_integer():
            return str(int(value))

        return f"{value:.12g}"

    return str(value)


# ============================================================
# CUSTOM CANVAS BUTTON
# ============================================================

class CalculatorButton(ButtonBehavior, Label):

    normal_color = ListProperty([0.12, 0.13, 0.16, 1])
    pressed_color = ListProperty([0.22, 0.23, 0.27, 1])

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = dp(21)

        with self.canvas.before:

            self.background_color = Color(
                *self.normal_color
            )

            self.background = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background,
            normal_color=self.update_color
        )

    def update_background(self, *args):

        self.background.pos = self.pos
        self.background.size = self.size

    def update_color(self, *args):

        self.background_color.rgba = self.normal_color

    def on_press(self):

        self.background_color.rgba = self.pressed_color

    def on_release(self):

        self.background_color.rgba = self.normal_color


# ============================================================
# CALCULATOR
# ============================================================

class Calculator(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10),
            **kwargs
        )

        Window.clearcolor = (
            0.035,
            0.04,
            0.05,
            1
        )

        self.expression = ""
        self.history = []

        self.create_display()
        self.create_keypad()

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    def create_display(self):

        display = BoxLayout(
            orientation="vertical",
            padding=[
                dp(10),
                dp(10),
                dp(10),
                dp(5)
            ],
            size_hint_y=0.27
        )

        self.expression_label = Label(
            text="",
            color=(0.50, 0.52, 0.57, 1),
            font_size=dp(18),
            halign="right",
            valign="bottom"
        )

        self.expression_label.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        display.add_widget(
            self.expression_label
        )

        self.result_label = Label(
            text="0",
            color=(1, 1, 1, 1),
            font_size=dp(43),
            halign="right",
            valign="middle",
            shorten=True,
            shorten_from="left"
        )

        self.result_label.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        display.add_widget(
            self.result_label
        )

        self.add_widget(display)

    # --------------------------------------------------------
    # BUTTON
    # --------------------------------------------------------

    def create_button(
        self,
        grid,
        text,
        function,
        color=None,
        pressed=None
    ):

        button = CalculatorButton(
            text=text,
            normal_color=color
            if color
            else [0.12, 0.13, 0.16, 1],
            pressed_color=pressed
            if pressed
            else [0.22, 0.23, 0.27, 1]
        )

        button.bind(
            on_release=function
        )

        grid.add_widget(button)

    # --------------------------------------------------------
    # KEYPAD
    # --------------------------------------------------------

    def create_keypad(self):

        keypad = GridLayout(
            cols=4,
            spacing=dp(8),
            size_hint_y=0.73
        )

        # Colors
        number = [0.12, 0.13, 0.16, 1]
        operation = [0.20, 0.22, 0.27, 1]
        red = [0.65, 0.12, 0.13, 1]
        blue = [0.10, 0.35, 0.75, 1]

        # Row 1
        self.create_button(
            keypad,
            "AC",
            lambda x: self.clear(),
            red
        )

        self.create_button(
            keypad,
            "DEL",
            lambda x: self.delete(),
            operation
        )

        self.create_button(
            keypad,
            "%",
            lambda x: self.percent(),
            operation
        )

        self.create_button(
            keypad,
            "÷",
            lambda x: self.add("÷"),
            operation
        )

        # Row 2
        self.create_button(
            keypad,
            "7",
            lambda x: self.add("7"),
            number
        )

        self.create_button(
            keypad,
            "8",
            lambda x: self.add("8"),
            number
        )

        self.create_button(
            keypad,
            "9",
            lambda x: self.add("9"),
            number
        )

        self.create_button(
            keypad,
            "×",
            lambda x: self.add("×"),
            operation
        )

        # Row 3
        self.create_button(
            keypad,
            "4",
            lambda x: self.add("4"),
            number
        )

        self.create_button(
            keypad,
            "5",
            lambda x: self.add("5"),
            number
        )

        self.create_button(
            keypad,
            "6",
            lambda x: self.add("6"),
            number
        )

        self.create_button(
            keypad,
            "−",
            lambda x: self.add("−"),
            operation
        )

        # Row 4
        self.create_button(
            keypad,
            "1",
            lambda x: self.add("1"),
            number
        )

        self.create_button(
            keypad,
            "2",
            lambda x: self.add("2"),
            number
        )

        self.create_button(
            keypad,
            "3",
            lambda x: self.add("3"),
            number
        )

        self.create_button(
            keypad,
            "+",
            lambda x: self.add("+"),
            operation
        )

        # Row 5
        self.create_button(
            keypad,
            "0",
            lambda x: self.add("0"),
            number
        )

        self.create_button(
            keypad,
            ".",
            lambda x: self.add("."),
            number
        )

        self.create_button(
            keypad,
            "H",
            lambda x: self.show_history(),
            operation
        )

        self.create_button(
            keypad,
            "=",
            lambda x: self.calculate(),
            blue
        )

        self.add_widget(keypad)

    # --------------------------------------------------------
    # INPUT
    # --------------------------------------------------------

    def add(self, value):

        if self.result_label.text == "Error":
            self.clear()

        self.expression += value

        self.expression_label.text = self.expression

        self.result_label.text = self.expression

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    def clear(self):

        self.expression = ""

        self.expression_label.text = ""

        self.result_label.text = "0"

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def delete(self):

        self.expression = self.expression[:-1]

        self.expression_label.text = self.expression

        if self.expression:
            self.result_label.text = self.expression
        else:
            self.result_label.text = "0"

    # --------------------------------------------------------
    # PERCENT
    # --------------------------------------------------------

    def percent(self):

        if not self.expression:
            return

        try:

            value = calculate_expression(
                self.expression
            )

            value = value / 100

            self.expression = format_number(value)

            self.expression_label.text = self.expression

            self.result_label.text = self.expression

        except Exception:

            self.result_label.text = "Error"

    # --------------------------------------------------------
    # CALCULATE
    # --------------------------------------------------------

    def calculate(self):

        if not self.expression:
            return

        try:

            original = self.expression

            answer = calculate_expression(
                original
            )

            answer = format_number(answer)

            self.history.append(
                original + " = " + answer
            )

            self.expression_label.text = original

            self.result_label.text = answer

            self.expression = answer

        except Exception:

            self.result_label.text = "Error"

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    def show_history(self):

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        scroll = ScrollView()

        history_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None
        )

        history_layout.bind(
            minimum_height=history_layout.setter(
                "height"
            )
        )

        if not self.history:

            history_layout.add_widget(
                Label(
                    text="No calculations yet",
                    font_size=dp(18),
                    color=(0.7, 0.7, 0.7, 1),
                    size_hint_y=None,
                    height=dp(50)
                )
            )

        else:

            for item in reversed(self.history):

                history_layout.add_widget(
                    Label(
                        text=item,
                        font_size=dp(17),
                        color=(1, 1, 1, 1),
                        size_hint_y=None,
                        height=dp(45),
                        halign="right"
                    )
                )

        scroll.add_widget(
            history_layout
        )

        layout.add_widget(scroll)

        clear_history = CalculatorButton(
            text="CLEAR HISTORY",
            size_hint_y=None,
            height=dp(55),
            normal_color=[0.65, 0.12, 0.13, 1],
            pressed_color=[0.8, 0.18, 0.19, 1]
        )

        layout.add_widget(clear_history)

        popup = Popup(
            title="Calculation History",
            content=layout,
            size_hint=(0.92, 0.75),
            separator_color=(0.10, 0.35, 0.75, 1)
        )

        def clear_history_function(instance):

            self.history.clear()
            popup.dismiss()

        clear_history.bind(
            on_release=clear_history_function
        )

        popup.open()


# ============================================================
# APP
# ============================================================

class CalculatorApp(App):

    def build(self):

        self.title = "Calculator"

        return Calculator()


if __name__ == "__main__":
    CalculatorApp().run()