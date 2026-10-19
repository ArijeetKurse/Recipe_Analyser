# Recipe Specification Language (RSL) Analyzer

A compiler design project that brings culinary recipes into the world of formal programming languages.

---

## What We Are Implementing Through This Code

Have you ever wondered how compilers like Python or GCC take raw text, spot errors, and turn written words into structured data? That is exactly what this project demonstrates—applied to cooking recipes!

We built a custom **Domain-Specific Language (DSL)** named the **Recipe Specification Language (RSL)** along with its dedicated compiler front-end. The system takes plain recipe text and runs it through two fundamental phases of compiler design:

1. **Lexical Analysis (The Lexer — `lexer.py`):**  
   Reads the source character by character, strips out whitespace and comments (`#` and `//`), and groups raw characters into meaningful **Tokens** (such as keywords `RECIPE`, `INGREDIENT`, identifiers, numbers, and symbols). If someone introduces an illegal symbol (like `@` or `$`), the lexer flags it as a **Lexical Error** with exact line and column coordinates.

2. **Syntax Analysis (The Parser — `parser.py`):**  
   Consumes the token stream and verifies whether it conforms to the formal grammatical rules of our language defined in **EBNF (Extended Backus-Naur Form)**. Using a hand-crafted **Recursive-Descent Parser**, it validates the recipe's structure—ensuring ingredients come before steps, mandatory punctuation like braces `{}` and semicolons `;` are present, and values match expected formats. If the syntax is valid, it constructs an **Abstract Syntax Tree (AST)** and displays a structured summary of the dish.

In short, it is an end-to-end compiler front-end that guarantees a recipe is structurally sound and valid before any cooking begins.

---

## Language Grammar (EBNF)

Our language follows a clean, deterministic context-free grammar:

```ebnf
Recipe          ::= "RECIPE" Identifier "{" RecipeBody "}"
RecipeBody      ::= IngredientList StepList [ ServeStatement ]
IngredientList  ::= IngredientDecl { IngredientDecl }
IngredientDecl  ::= "INGREDIENT" Identifier "=" Number [ Identifier ] ";"
StepList        ::= StepDecl { StepDecl }
StepDecl        ::= "STEP" StepContent ";"
StepContent     ::= StepItem { StepItem }
StepItem        ::= Identifier | Number | ","
ServeStatement  ::= "SERVE" Identifier ";"
```

---

## Project Structure

```text
Recipe_Analyser/
├── lexer.py          # Lexical Analyser (Tokenization & Lexical Error Detection)
├── parser.py         # Syntax Analyser (Recursive-Descent Parsing & AST Construction)
├── main.py           # CLI Entry Point, Interactive Menu & Demo Suite
├── requirements.txt  # Dependencies notice (Standard Library only)
├── examples/
│   ├── valid_recipe.txt    # Correct sample recipe
│   └── invalid_recipe.txt  # Sample with an intentional missing semicolon
└── README.md         # Project documentation
```

---

## Ways to Run the Code

You can run the analyzer in **three different ways**:

### 1. Interactive Menu Mode (Recommended)
The most convenient way to explore the project. Simply run:
```bash
python main.py
```
This launches an interactive terminal menu where you can choose samples, enter custom recipes, or run tests.

### 2. Direct File Mode (Command-Line Argument)
Analyze any `.txt` or `.rsl` recipe file directly by passing its path:
```bash
python main.py examples/valid_recipe.txt
```
To test error detection on a broken recipe:
```bash
python main.py examples/invalid_recipe.txt
```
*(The program exits with code `0` on success and `1` on failure, making it ideal for scripts or CI pipelines.)*

### 3. Automated Demonstration Suite
Run a batch of 11 curated edge-case tests (missing semicolons, misplaced steps, missing braces, illegal characters, empty inputs, etc.):
```bash
python main.py --demo
```

---

## How to Interact with the Code

When you launch the program via `python main.py`, you will see the interactive terminal interface:

```text
==================================================================
      RECIPE SPECIFICATION LANGUAGE (RSL) ANALYZER
==================================================================
 [1] Analyze Valid Sample Recipe
 [2] Analyze Invalid Sample Recipe
 [3] Analyze Custom File
 [4] Direct Text Input
 [5] Run Demonstration Suite
 [6] Exit
==================================================================
Enter choice (1-6):
```

Here is how each option works and how you interact with it:

- **Option `[1]` — Analyze Valid Sample Recipe:**  
  Type `1` and press **Enter**. The analyzer processes `examples/valid_recipe.txt`. It prints a full **Token Table** (token index, line, column, type, value), confirms lexical and syntax checks passed, and renders a formatted **Recipe Summary** with ingredients, quantities, units, and cooking steps.

- **Option `[2]` — Analyze Invalid Sample Recipe:**  
  Type `2` and press **Enter**. The analyzer processes `examples/invalid_recipe.txt` (which has a missing semicolon on line 8). You will see the token stream followed by a descriptive **Syntax Error** report highlighting the exact line, column, what was expected, and what was found.

- **Option `[3]` — Analyze Custom File:**  
  Type `3` and press **Enter**. The terminal will prompt: `Enter path:`. Type the relative or absolute path to your file (for example, `examples/valid_recipe.txt` or your own recipe file) and hit **Enter**.

- **Option `[4]` — Direct Text Input:**  
  Type `4` and press **Enter**. You can now type or paste a multi-line recipe directly into the terminal. Once you are done, type `END` on a brand-new line and press **Enter**. The analyzer immediately parses your text and displays the results.

- **Option `[5]` — Run Demonstration Suite:**  
  Type `5` and press **Enter**. The suite executes 11 predefined test scenarios one after another, showcasing both valid recipes and every error condition handled by the lexer and parser.

- **Option `[6]` — Exit:**  
  Type `6` and press **Enter** to exit the program.

*Tip: After viewing the output of any option, press **Enter** when prompted to return to the main menu.*

---

## Libraries Used in This Project

This project was built with **zero external third-party dependencies** to remain completely lightweight, portable, and transparent. It relies exclusively on the **Python Standard Library**:

1. **`sys`**  
   - Reads command-line arguments via `sys.argv` (to support direct file arguments and the `--demo` flag).
   - Manages exit status codes (`sys.exit(0)` for successful validation, `sys.exit(1)` for errors).

2. **`os`**  
   - Handles cross-platform filesystem paths (`os.path.join`, `os.path.dirname`).
   - Checks whether user-specified recipe files exist on disk before reading (`os.path.exists`).

3. **`typing`** (`List`, `Tuple`, `Optional`, `Any`)  
   - Supplies static type hints across `lexer.py`, `parser.py`, and `main.py`.
   - Ensures strict type safety, making token structures, AST nodes, and return signatures clear and self-documenting.

4. **`enum`** (`Enum`)  
   - Provides the base class for `TokenType` in `lexer.py`, categorizing language keywords (`RECIPE`, `INGREDIENT`, `STEP`, `SERVE`), literals (`IDENTIFIER`, `NUMBER`), symbols (`=`, `;`, `,`, `{`, `}`), and end-of-file (`EOF`).

No `pip install` commands are needed—any environment running Python 3.8+ can execute the code immediately!
