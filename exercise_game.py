import random
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from exercise_generator import LANG_FROM, LANG_TO, generate_exercise


EXERCISE_TYPES = (
    "matching",
    "single_word_translation",
    "translation",
    "fill_in_blank",
)
BEGINNER_EXERCISE_TYPES = ("matching", "single_word_translation")
EXERCISE_TYPE_LABELS = {
    "random": "Random",
    "matching": "Matching",
    "single_word_translation": "Single word translation",
    "translation": "Translation",
    "fill_in_blank": "Fill in the blank",
}
LANGUAGE_DIRECTIONS = (
    (LANG_FROM, LANG_TO),
    (LANG_TO, LANG_FROM),
)


class ExerciseGame:
    COLORS = {
        "background": "#17161D",
        "panel": "#22212A",
        "panel_alt": "#2B2934",
        "input": "#302E3A",
        "text": "#F1EFF7",
        "muted": "#AAA6B8",
        "purple": "#8B6CE8",
        "purple_hover": "#A184F5",
        "success": "#78D6A3",
        "error": "#FF8D9A",
    }

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Language Exercise Game")
        self.root.geometry("1920x1080")
        self.root.minsize(660, 540)
        self.root.configure(background=self.COLORS["background"])
        self._setup_styles()

        self.level_var = tk.StringVar(value="1")
        self.exercise_type_var = tk.StringVar(value=EXERCISE_TYPE_LABELS["random"])
        self.status_var = tk.StringVar(value="Choose a level and exercise type to begin.")
        self.score_var = tk.StringVar()
        self.exercise: dict | None = None
        self.lang_from = "English"
        self.lang_to = "Norwegian"
        self.matching_pairs: list[list[str]] = []
        self.matching_targets: list[str] = []
        self.matching_answer_vars: list[tk.StringVar] = []
        self.matching_selects: list[ttk.Combobox] = []
        self.matching_result_labels: list[ttk.Label] = []

        app_frame = ttk.Frame(root, style="App.TFrame", padding=(24, 20))
        app_frame.pack(fill="both", expand=True)

        header = ttk.Frame(app_frame, style="App.TFrame")
        header.pack(fill="x", pady=(0, 18))
        ttk.Label(header, text="LANGUAGE ARCADE", style="Eyebrow.TLabel").pack(
            anchor="w"
        )
        ttk.Label(header, text="Practice a little. Learn a lot.", style="Title.TLabel").pack(
            anchor="w", pady=(3, 2)
        )
        ttk.Label(
            header,
            text="Build your vocabulary one exercise at a time.",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        controls = ttk.Frame(app_frame, style="Card.TFrame", padding=18)
        controls.pack(fill="x", pady=(0, 14))

        ttk.Label(controls, text="Level", style="Card.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.level_select = ttk.Combobox(
            controls,
            textvariable=self.level_var,
            values=tuple(str(level) for level in range(1, 11)),
            state="readonly",
            width=8,
        )
        self.level_select.grid(row=1, column=0, padx=(0, 16), pady=(6, 0), sticky="w")
        self.level_select.bind("<<ComboboxSelected>>", self._on_level_selected)

        ttk.Label(controls, text="Exercise type", style="Card.TLabel").grid(
            row=0, column=1, sticky="w"
        )
        self.type_select = ttk.Combobox(
            controls,
            textvariable=self.exercise_type_var,
            state="readonly",
            width=28,
        )
        self.type_select.grid(row=1, column=1, padx=(0, 16), pady=(6, 0), sticky="w")

        self.generate_button = ttk.Button(
            controls,
            text="New exercise",
            command=self._generate,
            style="Accent.TButton",
        )
        self.generate_button.grid(row=1, column=2, pady=(6, 0), sticky="w")

        progress = ttk.Frame(app_frame, style="App.TFrame")
        progress.pack(fill="x", pady=(0, 10))
        ttk.Label(
            progress, textvariable=self.status_var, style="Status.TLabel"
        ).pack(side="left", anchor="w")
        ttk.Label(
            progress, textvariable=self.score_var, style="Score.TLabel"
        ).pack(side="right", anchor="e")
        self.game_frame = ttk.Frame(
            app_frame, style="Card.TFrame", padding=(20, 18)
        )
        self.game_frame.pack(fill="both", expand=True)

        self._update_exercise_types()

    def _setup_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "App.TFrame",
            background=self.COLORS["background"],
        )
        style.configure(
            "Card.TFrame",
            background=self.COLORS["panel"],
        )
        style.configure(
            "MatchRow.TFrame",
            background=self.COLORS["panel_alt"],
        )
        style.configure(
            "TLabel",
            background=self.COLORS["background"],
            foreground=self.COLORS["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Card.TLabel",
            background=self.COLORS["panel"],
            foreground=self.COLORS["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Card.Subtitle.TLabel",
            background=self.COLORS["panel"],
            foreground=self.COLORS["muted"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "MatchRow.TLabel",
            background=self.COLORS["panel_alt"],
            foreground=self.COLORS["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Eyebrow.TLabel",
            background=self.COLORS["background"],
            foreground=self.COLORS["purple_hover"],
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Title.TLabel",
            background=self.COLORS["background"],
            foreground=self.COLORS["text"],
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.COLORS["background"],
            foreground=self.COLORS["muted"],
        )
        style.configure(
            "Status.TLabel",
            background=self.COLORS["background"],
            foreground=self.COLORS["muted"],
        )
        style.configure(
            "Score.TLabel",
            background=self.COLORS["background"],
            foreground=self.COLORS["purple_hover"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "TButton",
            background=self.COLORS["panel_alt"],
            foreground=self.COLORS["text"],
            padding=(12, 8),
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "TButton",
            background=[
                ("disabled", self.COLORS["panel_alt"]),
                ("active", self.COLORS["purple_hover"]),
            ],
            foreground=[("disabled", self.COLORS["muted"])],
        )
        style.configure(
            "Accent.TButton",
            background=self.COLORS["purple"],
            foreground="#FFFFFF",
        )
        style.map(
            "Accent.TButton",
            background=[
                ("disabled", self.COLORS["panel_alt"]),
                ("active", self.COLORS["purple_hover"]),
            ],
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.COLORS["input"],
            background=self.COLORS["input"],
            foreground=self.COLORS["text"],
            arrowcolor=self.COLORS["purple_hover"],
            padding=6,
        )
        style.configure(
            "TEntry",
            fieldbackground=self.COLORS["input"],
            foreground=self.COLORS["text"],
            insertcolor=self.COLORS["text"],
            padding=7,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.COLORS["input"])],
            foreground=[("readonly", self.COLORS["text"])],
            selectbackground=[("readonly", self.COLORS["input"])],
            selectforeground=[("readonly", self.COLORS["text"])],
        )
        self.root.option_add("*TCombobox*Listbox.background", self.COLORS["input"])
        self.root.option_add("*TCombobox*Listbox.foreground", self.COLORS["text"])
        self.root.option_add(
            "*TCombobox*Listbox.selectBackground", self.COLORS["purple"]
        )
        self.root.option_add(
            "*TCombobox*Listbox.selectForeground", "#FFFFFF"
        )

    def _available_types(self) -> tuple[str, ...]:
        if int(self.level_var.get()) <= 3:
            return BEGINNER_EXERCISE_TYPES
        return EXERCISE_TYPES

    def _on_level_selected(self, event: tk.Event) -> None:
        if event.widget is self.level_select:
            self._update_exercise_types()

    def _update_exercise_types(self) -> None:
        values = tuple(
            EXERCISE_TYPE_LABELS[exercise_type]
            for exercise_type in ("random", *self._available_types())
        )
        self.type_select.configure(values=values)
        if self.exercise_type_var.get() not in values:
            self.exercise_type_var.set(EXERCISE_TYPE_LABELS["random"])

    def _generate(self) -> None:
        level = int(self.level_var.get())
        selected_type = self.exercise_type_var.get()
        available_types = self._available_types()
        lang_from, lang_to = random.choice(LANGUAGE_DIRECTIONS)
        exercise_type = (
            random.choice(available_types)
            if selected_type == EXERCISE_TYPE_LABELS["random"]
            else next(
                exercise_type
                for exercise_type in available_types
                if EXERCISE_TYPE_LABELS[exercise_type] == selected_type
            )
        )

        self.generate_button.configure(state="disabled")
        self.status_var.set(f"Generating {lang_from} to {lang_to} exercise...")
        self.score_var.set("")
        thread = threading.Thread(
            target=self._generate_in_background,
            args=(level, exercise_type, lang_from, lang_to),
            daemon=True,
        )
        thread.start()

    def _generate_in_background(
        self, level: int, exercise_type: str, lang_from: str, lang_to: str
    ) -> None:
        try:
            exercise = generate_exercise(
                level,
                exercise_type,
                lang_from=lang_from,
                lang_to=lang_to,
            )
            if not isinstance(exercise, dict):
                raise RuntimeError("The AI did not return a valid exercise.")
        except Exception as error:
            self.root.after(0, self._show_generation_error, str(error))
            return

        self.root.after(0, self._display_exercise, exercise, lang_from, lang_to)

    def _show_generation_error(self, error: str) -> None:
        self.generate_button.configure(state="normal")
        self.status_var.set("Could not generate an exercise.")
        messagebox.showerror("Exercise error", error, parent=self.root)

    def _display_exercise(
        self, exercise: dict, lang_from: str, lang_to: str
    ) -> None:
        self.generate_button.configure(state="normal")
        self.exercise = exercise
        self.lang_from = lang_from
        self.lang_to = lang_to
        self._clear_game_frame()

        exercise_type = exercise.get("exercise_type")
        if exercise_type == "matching":
            pairs = exercise.get("pairs")
            if not isinstance(pairs, list) or not pairs or any(
                not isinstance(pair, list)
                or len(pair) != 2
                or not all(isinstance(word, str) and word.strip() for word in pair)
                for pair in pairs
            ):
                self._show_generation_error("The AI returned invalid matching pairs.")
                return
            self.matching_pairs = pairs
            self.matching_targets = [pair[1] for pair in pairs]
            random.shuffle(self.matching_targets)
            self.status_var.set(
                f"Match {lang_from} words to their {lang_to} translations."
            )
            self._show_matching_question()
        elif exercise_type in ("single_word_translation", "translation", "fill_in_blank"):
            question = exercise.get(
                "sentence_with_blank" if exercise_type == "fill_in_blank" else "question"
            )
            answer = exercise.get("answer")
            if not isinstance(question, str) or not question.strip() or not isinstance(
                answer, str
            ) or not answer.strip():
                self._show_generation_error("The AI returned an incomplete exercise.")
                return
            self.status_var.set("Enter your answer, then check it.")
            self._show_translation_question(exercise_type, question, answer)
        else:
            self._show_generation_error("The AI returned an unsupported exercise type.")

    def _show_matching_question(self) -> None:
        self._clear_game_frame()
        ttk.Label(
            self.game_frame,
            text="Match all the pairs",
            style="Card.TLabel",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            self.game_frame,
            text=(
                f"Choose a {self.lang_to} translation for every {self.lang_from} "
                "word, then check your matches."
            ),
            style="Card.Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 16))

        self.matching_answer_vars = []
        self.matching_selects = []
        self.matching_result_labels = []
        for pair in self.matching_pairs:
            source = pair[0]
            row = ttk.Frame(
                self.game_frame, style="MatchRow.TFrame", padding=(12, 9)
            )
            row.pack(fill="x", pady=4)
            ttk.Label(
                row,
                text=source,
                style="MatchRow.TLabel",
                font=("Segoe UI", 11, "bold"),
            ).grid(row=0, column=0, sticky="w", padx=(0, 16))
            ttk.Label(
                row,
                text="→",
                style="MatchRow.TLabel",
                foreground=self.COLORS["purple_hover"],
            ).grid(row=0, column=1, padx=(0, 16))

            answer_var = tk.StringVar()
            target_select = ttk.Combobox(
                row,
                textvariable=answer_var,
                values=self.matching_targets,
                state="readonly",
                width=30,
            )
            target_select.grid(row=0, column=2, sticky="ew")
            target_select.bind(
                "<<ComboboxSelected>>", self._on_matching_selection
            )
            row.columnconfigure(2, weight=1)
            result_label = ttk.Label(row, text="", style="MatchRow.TLabel")
            result_label.grid(row=0, column=3, sticky="e", padx=(12, 0))

            self.matching_answer_vars.append(answer_var)
            self.matching_selects.append(target_select)
            self.matching_result_labels.append(result_label)

        self.matching_check_button = ttk.Button(
            self.game_frame,
            text="Check all matches",
            style="Accent.TButton",
            command=self._check_matching_answers,
            state="disabled",
        )
        self.matching_check_button.pack(anchor="e", pady=(16, 0))

    def _on_matching_selection(self, event: tk.Event) -> None:
        if event.widget in self.matching_selects:
            self._update_matching_button()

    def _update_matching_button(self) -> None:
        all_selected = bool(self.matching_answer_vars) and all(
            answer.get().strip() for answer in self.matching_answer_vars
        )
        self.matching_check_button.configure(
            state="normal" if all_selected else "disabled"
        )

    def _check_matching_answers(self) -> None:
        correct_count = 0
        for pair, answer, result_label, target_select in zip(
            self.matching_pairs,
            self.matching_answer_vars,
            self.matching_result_labels,
            self.matching_selects,
        ):
            expected = pair[1]
            is_correct = answer.get().strip().casefold() == expected.strip().casefold()
            if is_correct:
                correct_count += 1
                result_label.configure(
                    text="Correct",
                    foreground=self.COLORS["success"],
                )
            else:
                result_label.configure(
                    text=f"Answer: {expected}",
                    foreground=self.COLORS["error"],
                )
            target_select.configure(state="disabled")

        self.matching_check_button.configure(state="disabled")
        total = len(self.matching_pairs)
        self.score_var.set(f"{correct_count} / {total} correct")
        self.status_var.set(
            "Perfect! Every match is correct."
            if correct_count == total
            else "Check the answers shown beside each word."
        )

    def _show_translation_question(
        self, exercise_type: str, question: str, answer: str
    ) -> None:
        if exercise_type == "single_word_translation":
            direction = f"Translate this word from {self.lang_from} to {self.lang_to}:"
        elif exercise_type == "fill_in_blank":
            direction = f"Fill in the {self.lang_to} blank:"
        elif exercise_type == "translation":
            direction = f"Translate from {self.lang_from} to {self.lang_to}:"
        else:
            direction = "Your question:"
        ttk.Label(
            self.game_frame,
            text=direction,
            style="Card.TLabel",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", pady=(8, 4))
        ttk.Label(
            self.game_frame,
            text=question,
            style="Card.TLabel",
            font=("Segoe UI", 16),
        ).pack(anchor="w", pady=(0, 12))

        answer_var = tk.StringVar()
        answer_entry = ttk.Entry(self.game_frame, textvariable=answer_var, width=36)
        answer_entry.pack(anchor="w")
        answer_entry.focus_set()

        feedback = ttk.Label(self.game_frame, text="", style="Card.TLabel")
        feedback.pack(anchor="w", pady=10)

        def check_answer() -> None:
            if answer_var.get().strip().casefold() == answer.strip().casefold():
                feedback.configure(text="Correct!", foreground="green")
                self.score_var.set("Score: 1/1")
            else:
                feedback.configure(text=f"Not quite. The answer is: {answer}")
                self.score_var.set("Score: 0/1")
            check_button.configure(state="disabled")
            answer_entry.configure(state="disabled")

        check_button = ttk.Button(
            self.game_frame, text="Check answer", command=check_answer
        )
        check_button.pack(anchor="w", pady=(8, 0))

        hint = self.exercise.get("hint", "") if self.exercise else ""
        if isinstance(hint, str) and hint.strip():
            ttk.Label(
                self.game_frame,
                text=f"Hint: {hint}",
                wraplength=480,
                style="Card.Subtitle.TLabel",
            ).pack(anchor="w", pady=(12, 0))

        def check_on_enter(event: tk.Event) -> str:
            if event.keysym == "Return":
                check_answer()
            return "break"

        answer_entry.bind("<Return>", check_on_enter)

    def _clear_game_frame(self) -> None:
        for child in self.game_frame.winfo_children():
            child.destroy()


def main() -> None:
    root = tk.Tk()
    ExerciseGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
