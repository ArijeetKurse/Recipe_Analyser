"""
main.py - Entry Point for Recipe Specification Language (RSL) Analyzer
"""

import sys
import os
from typing import List
from lexer import Lexer, Token, TokenType
from parser import Parser, ParseError, RecipeNode


def print_banner() -> None:
    print("=" * 66)
    print("      RECIPE SPECIFICATION LANGUAGE (RSL) ANALYZER")
    print("=" * 66)


def display_tokens(tokens: List[Token]) -> None:
    print("\n" + "-" * 66)
    print(f"{'#':<4} {'Line':<6} {'Col':<6} {'Token Type':<16} {'Token Value'}")
    print("-" * 66)
    for i, tok in enumerate(tokens, 1):
        val = repr(tok.value)
        print(f"{i:<4} {tok.line:<6} {tok.column:<6} {tok.type.name:<16} {val[:28]}")
    print("-" * 66)


def display_recipe_summary(ast: RecipeNode) -> None:
    print(f"\nRECIPE SUMMARY: {ast.name.upper()}\n" + "-" * 40)
    print("Ingredients:")
    for i, ing in enumerate(ast.ingredients, 1):
        unit = f" {ing.unit}" if ing.unit else ""
        print(f"  {i}. {ing.name:<16} : {ing.quantity}{unit}")
    print("\nCooking Steps:")
    for s, step in enumerate(ast.steps, 1):
        print(f"  {s}. {step.description}")
    print(f"\nServe: {ast.serve.dish_name if ast.serve else '(None)'}\n" + "=" * 66)


def analyze_recipe(source_code: str, title: str = "Recipe") -> bool:
    print(f"\n>>> Analyzing: {title}")
    tokens, lexical_errors = Lexer(source_code).tokenize()
    display_tokens(tokens)

    if lexical_errors:
        print("\n[!] LEXICAL ANALYSIS FAILED:")
        for err in lexical_errors:
            print(f"  --> {err}")
        print("\n[VALIDATION RESULT]: INVALID RECIPE (Lexical Errors)")
        return False

    print("[*] Lexical Analysis Passed.")
    try:
        ast = Parser(tokens).parse()
    except ParseError as pe:
        print(f"\n[!] SYNTAX ANALYSIS FAILED:\n  --> {pe}")
        print("\n[VALIDATION RESULT]: INVALID RECIPE (Syntax Errors)")
        return False

    print("\n[OK] SYNTAX ANALYSIS PASSED!\n[VALIDATION RESULT]: VALID RECIPE")
    display_recipe_summary(ast)
    return True


def analyze_file(filepath: str) -> bool:
    if not os.path.exists(filepath):
        print(f"\n[Error]: File not found: '{filepath}'")
        return False
    with open(filepath, "r", encoding="utf-8") as f:
        return analyze_recipe(f.read(), title=f"File: {filepath}")


def run_demonstration_suite() -> None:
    demos = [
        ("Valid Recipe", "RECIPE Pancakes {\n  INGREDIENT flour = 2 cups;\n  STEP Mix flour;\n  SERVE Pancakes;\n}"),
        ("Missing Semicolon", "RECIPE Omelette {\n  INGREDIENT eggs = 2\n  STEP Beat eggs;\n}"),
        ("Missing Equals", "RECIPE Toast {\n  INGREDIENT bread 2 slices;\n  STEP Toast bread;\n}"),
        ("Missing Opening Brace", "RECIPE Salad\n  INGREDIENT lettuce = 1 bowl;\n  STEP Toss;\n}"),
        ("Missing Closing Brace", "RECIPE Tea {\n  INGREDIENT water = 1 cup;\n  STEP Boil;"),
        ("Missing Recipe Name", "RECIPE {\n  INGREDIENT sugar = 1 cup;\n  STEP Stir;\n}"),
        ("Invalid Character", "RECIPE Cake @ {\n  INGREDIENT flour = 1 cup;\n  STEP Bake;\n}"),
        ("Missing Quantity", "RECIPE Soup {\n  INGREDIENT salt = ;\n  STEP Simmer;\n}"),
        ("Empty Input", "# Just comments"),
        ("Trailing Content", "RECIPE Coffee {\n  INGREDIENT beans = 10 grams;\n  STEP Brew;\n}\nEXTRA"),
        ("Multiple Items", "RECIPE Salad {\n  INGREDIENT apple = 2;\n  INGREDIENT honey = 1 tbsp;\n  STEP Chop apple;\n  STEP Mix with honey;\n  SERVE Salad;\n}"),
    ]
    for name, code in demos:
        print(f"\n{'#' * 66}\n DEMO TEST: {name}\n{'#' * 66}")
        analyze_recipe(code, title=name)


def run_interactive_mode() -> None:
    base = os.path.dirname(__file__)
    samples = {
        "1": os.path.join(base, "examples", "valid_recipe.txt"),
        "2": os.path.join(base, "examples", "invalid_recipe.txt"),
    }
    while True:
        print_banner()
        print(" [1] Analyze Valid Sample Recipe\n [2] Analyze Invalid Sample Recipe\n [3] Analyze Custom File\n [4] Direct Text Input\n [5] Run Demonstration Suite\n [6] Exit\n" + "=" * 66)
        choice = input("Enter choice (1-6): ").strip()
        if choice in samples:
            analyze_file(samples[choice])
        elif choice == "3":
            path = input("Enter path: ").strip()
            if path: analyze_file(path)
        elif choice == "4":
            print("Enter recipe text (enter 'END' on a new line to finish):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END": break
                lines.append(line)
            analyze_recipe("\n".join(lines), title="User Input")
        elif choice == "5":
            run_demonstration_suite()
        elif choice == "6":
            print("Goodbye!")
            break
        input("\nPress Enter to continue...")


def main() -> None:
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("-h", "--help"):
            print("Usage: python main.py [<recipe_path> | --demo]")
        elif arg == "--demo":
            run_demonstration_suite()
        else:
            sys.exit(0 if analyze_file(arg) else 1)
    else:
        run_interactive_mode()


if __name__ == "__main__":
    main()
