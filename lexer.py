"""
lexer.py - Lexical Analyser for Recipe Specification Language (RSL)
"""

from enum import Enum
from typing import List, Tuple, Any, Optional


class TokenType(Enum):
    RECIPE, INGREDIENT, STEP, SERVE = "RECIPE", "INGREDIENT", "STEP", "SERVE"
    IDENTIFIER, NUMBER = "IDENTIFIER", "NUMBER"
    EQUALS, SEMICOLON, COMMA, LBRACE, RBRACE, EOF = "=", ";", ",", "{", "}", "EOF"


KEYWORDS = {t.value: t for t in (TokenType.RECIPE, TokenType.INGREDIENT, TokenType.STEP, TokenType.SERVE)}
SYMBOLS = {"=": TokenType.EQUALS, ";": TokenType.SEMICOLON, ",": TokenType.COMMA, "{": TokenType.LBRACE, "}": TokenType.RBRACE}


class Token:
    def __init__(self, token_type: TokenType, value: Any, line: int, column: int):
        self.type, self.value, self.line, self.column = token_type, value, line, column

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, Line: {self.line}, Col: {self.column})"

    def __str__(self) -> str:
        return f"{self.type.name:<12} {repr(self.value):<18} (Line {self.line}, Col {self.column})"


class LexicalError:
    def __init__(self, message: str, line: int, column: int, character: str = ""):
        self.message, self.line, self.column, self.character = message, line, column, character

    def __str__(self) -> str:
        return f"[Lexical Error] Line {self.line}, Column {self.column}: {self.message}"


class Lexer:
    def __init__(self, source_code: str):
        self.source = source_code.replace("\r\n", "\n").replace("\r", "\n")
        self.pos, self.line, self.col, self.length = 0, 1, 1, len(self.source)

    def _peek(self, offset: int = 0) -> Optional[str]:
        p = self.pos + offset
        return self.source[p] if p < self.length else None

    def _advance(self) -> Optional[str]:
        if self.pos >= self.length:
            return None
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def tokenize(self) -> Tuple[List[Token], List[LexicalError]]:
        tokens, errors = [], []
        while self.pos < self.length:
            # Skip whitespace
            if self._peek().isspace():
                self._advance()
                continue

            # Skip comments (# or //)
            if self._peek() == "#" or (self._peek() == "/" and self._peek(1) == "/"):
                while self._peek() and self._peek() != "\n":
                    self._advance()
                continue

            s_line, s_col, ch = self.line, self.col, self._peek()

            # Identifiers and keywords
            if ch.isalpha() or ch == "_":
                ident = []
                while self._peek() and (self._peek().isalnum() or self._peek() == "_"):
                    ident.append(self._advance())
                text = "".join(ident)
                tokens.append(Token(KEYWORDS.get(text, TokenType.IDENTIFIER), text, s_line, s_col))
            # Integer numbers
            elif ch.isdigit():
                num = []
                while self._peek() and self._peek().isdigit():
                    num.append(self._advance())
                tokens.append(Token(TokenType.NUMBER, int("".join(num)), s_line, s_col))
            # Symbols
            elif ch in SYMBOLS:
                tokens.append(Token(SYMBOLS[ch], ch, s_line, s_col))
                self._advance()
            # Unexpected character
            else:
                bad_char = self._advance()
                errors.append(LexicalError(f"Unexpected character '{bad_char}'", s_line, s_col, bad_char or ""))

        tokens.append(Token(TokenType.EOF, "EOF", self.line, self.col))
        return tokens, errors
