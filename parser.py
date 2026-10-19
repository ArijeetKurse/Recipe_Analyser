"""
parser.py - Syntax Analyser for Recipe Specification Language (RSL)
"""

from typing import List, Optional
from lexer import Token, TokenType


class ParseError(Exception):
    def __init__(self, message: str, line: int, column: int, found_token: Optional[Token] = None):
        super().__init__(message)
        self.message, self.line, self.column, self.found_token = message, line, column, found_token

    def __str__(self) -> str:
        return f"[Syntax Error] Line {self.line}, Column {self.column}: {self.message}"


class ASTNode:
    pass


class IngredientNode(ASTNode):
    def __init__(self, name: str, quantity: int, unit: Optional[str], line: int, column: int):
        self.name, self.quantity, self.unit, self.line, self.column = name, quantity, unit, line, column

    def __repr__(self) -> str:
        return f"Ingredient({self.name} = {self.quantity}{' ' + self.unit if self.unit else ''})"


class StepNode(ASTNode):
    def __init__(self, description: str, line: int, column: int):
        self.description, self.line, self.column = description, line, column

    def __repr__(self) -> str:
        return f"Step({repr(self.description)})"


class ServeNode(ASTNode):
    def __init__(self, dish_name: str, line: int, column: int):
        self.dish_name, self.line, self.column = dish_name, line, column

    def __repr__(self) -> str:
        return f"Serve({self.dish_name})"


class RecipeNode(ASTNode):
    def __init__(
        self,
        name: str,
        ingredients: List[IngredientNode],
        steps: List[StepNode],
        serve: Optional[ServeNode],
        line: int,
        column: int,
    ):
        self.name, self.ingredients, self.steps, self.serve = name, ingredients, steps, serve
        self.line, self.column = line, column


class Parser:
    """
    Recursive-Descent Parser for RSL.

    EBNF Grammar:
        Recipe         ::= "RECIPE" Identifier "{" RecipeBody "}"
        RecipeBody     ::= IngredientList StepList [ ServeStatement ]
        IngredientList ::= IngredientDecl { IngredientDecl }
        IngredientDecl ::= "INGREDIENT" Identifier "=" Number [ Identifier ] ";"
        StepList       ::= StepDecl { StepDecl }
        StepDecl       ::= "STEP" StepContent ";"
        StepContent    ::= StepItem { StepItem }
        StepItem       ::= Identifier | Number | ","
        ServeStatement ::= "SERVE" Identifier ";"
    """

    def __init__(self, tokens: List[Token]):
        self.tokens, self.idx = tokens, 0

    @property
    def current(self) -> Token:
        return self.tokens[self.idx] if self.idx < len(self.tokens) else self.tokens[-1]

    def _advance(self) -> Token:
        tok = self.current
        if self.idx < len(self.tokens) - 1:
            self.idx += 1
        return tok

    def _expect(self, expected_type: TokenType, err: Optional[str] = None) -> Token:
        tok = self.current
        if tok.type != expected_type:
            msg = err or f"Expected '{expected_type.value}', but found '{tok.value}'."
            raise ParseError(msg, tok.line, tok.column, tok)
        return self._advance()

    def parse(self) -> RecipeNode:
        if not self.tokens or (len(self.tokens) == 1 and self.tokens[0].type == TokenType.EOF):
            tok = self.tokens[0] if self.tokens else Token(TokenType.EOF, "EOF", 1, 1)
            raise ParseError("Recipe is empty. Expected 'RECIPE' declaration.", tok.line, tok.column, tok)

        r_kw = self._expect(
            TokenType.RECIPE,
            f"Expected 'RECIPE' keyword at start of recipe, but found '{self.current.value}'.",
        )
        name_tok = self._expect(
            TokenType.IDENTIFIER,
            f"Expected recipe name (identifier) after 'RECIPE', but found '{self.current.value}'.",
        )
        self._expect(
            TokenType.LBRACE,
            f"Expected '{{' after recipe name '{name_tok.value}', but found '{self.current.value}'.",
        )

        # Ingredients (at least one required)
        if self.current.type != TokenType.INGREDIENT:
            raise ParseError(
                f"Expected at least one 'INGREDIENT' declaration in recipe, but found '{self.current.value}'.",
                self.current.line,
                self.current.column,
                self.current,
            )
        ingredients: List[IngredientNode] = []
        while self.current.type == TokenType.INGREDIENT:
            ingredients.append(self._parse_ingredient())

        # Steps (at least one required)
        if self.current.type != TokenType.STEP:
            raise ParseError(
                f"Expected at least one 'STEP' declaration after ingredients, but found '{self.current.value}'.",
                self.current.line,
                self.current.column,
                self.current,
            )
        steps: List[StepNode] = []
        while self.current.type == TokenType.STEP:
            steps.append(self._parse_step())

        # Optional Serve
        serve = self._parse_serve() if self.current.type == TokenType.SERVE else None

        # Check for misplaced declarations
        if self.current.type == TokenType.INGREDIENT:
            raise ParseError(
                "Misplaced 'INGREDIENT' declaration. All ingredients must be declared before cooking steps.",
                self.current.line,
                self.current.column,
                self.current,
            )
        if self.current.type == TokenType.STEP:
            raise ParseError(
                "Misplaced 'STEP' declaration. Cooking steps cannot appear after 'SERVE'.",
                self.current.line,
                self.current.column,
                self.current,
            )

        # Closing brace
        if self.current.type == TokenType.EOF:
            raise ParseError(
                "Expected '}' to close recipe definition, but reached end of file.",
                self.current.line,
                self.current.column,
                self.current,
            )
        self._expect(TokenType.RBRACE, f"Expected '}}' to close recipe definition, but found '{self.current.value}'.")

        # Reject trailing content
        if self.current.type != TokenType.EOF:
            raise ParseError(
                f"Unexpected content after recipe closing brace: '{self.current.value}'.",
                self.current.line,
                self.current.column,
                self.current,
            )

        return RecipeNode(name_tok.value, ingredients, steps, serve, r_kw.line, r_kw.column)

    def _parse_ingredient(self) -> IngredientNode:
        start = self._expect(TokenType.INGREDIENT)
        name = self._expect(
            TokenType.IDENTIFIER,
            f"Expected ingredient name (identifier) after 'INGREDIENT', but found '{self.current.value}'.",
        ).value
        self._expect(TokenType.EQUALS, f"Expected '=' after ingredient name '{name}', but found '{self.current.value}'.")
        qty = self._expect(
            TokenType.NUMBER,
            f"Expected ingredient quantity (integer) after '=' for ingredient '{name}', but found '{self.current.value}'.",
        ).value
        unit = self._advance().value if self.current.type == TokenType.IDENTIFIER else None
        self._expect(
            TokenType.SEMICOLON,
            f"Expected ';' at the end of ingredient declaration for '{name}', but found '{self.current.value}'.",
        )
        return IngredientNode(name, qty, unit, start.line, start.column)

    def _parse_step(self) -> StepNode:
        start = self._expect(TokenType.STEP)
        if self.current.type == TokenType.SEMICOLON:
            raise ParseError(
                "Step description cannot be empty. Expected action details before ';'.",
                self.current.line,
                self.current.column,
                self.current,
            )

        words = []
        while self.current.type in (TokenType.IDENTIFIER, TokenType.NUMBER, TokenType.COMMA):
            tok = self._advance()
            if tok.type == TokenType.COMMA and words:
                words[-1] += ","
            else:
                words.append(str(tok.value))

        self._expect(TokenType.SEMICOLON, f"Expected ';' at the end of STEP declaration, but found '{self.current.value}'.")
        return StepNode(" ".join(words), start.line, start.column)

    def _parse_serve(self) -> ServeNode:
        start = self._expect(TokenType.SERVE)
        dish = self._expect(
            TokenType.IDENTIFIER,
            f"Expected dish name (identifier) to serve after 'SERVE', but found '{self.current.value}'.",
        ).value
        self._expect(TokenType.SEMICOLON, f"Expected ';' after 'SERVE {dish}', but found '{self.current.value}'.")
        return ServeNode(dish, start.line, start.column)
