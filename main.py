"""
    Basic example showing how to read and validate data from a file using PyDantic.
"""

import json
import pydantic
from typing import Optional, List


class ISBN10FormatError(Exception):
    """Custom error for invalid ISBN-10 format."""

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


class ISBNMissingError(Exception):
    """Custom error for missing ISBN."""

    def __init__(self, title: str, message: str) -> None:
        self.title = title
        self.message = message
        super().__init__(message)


class Book(pydantic.BaseModel):
    title: str
    author: str
    publisher: str
    price: float
    isbn_10: Optional[str]
    isbn_13: Optional[str]
    subtitle: Optional[str]

    @pydantic.root_validator(pre=True)
    @classmethod
    def check_isbn10_and_isbn13(cls, values):
        if "isbn_10" not in values and "isbn_13" not in values:
            raise ISBNMissingError(
                title=values["title"], message="Must have at least one ISBN."
            )
        return values

    @pydantic.validator("isbn_10")
    @classmethod
    def isbn_10_validator(cls, value: str) -> str:
        """Validator for ISBN-10 attribute."""
        chars = [char for char in value if char.isdigit() or char in "Xx"]
        if len(chars) != 10:
            raise ISBN10FormatError(value=value, message="ISBN-10 must be 10 digits.")

        def char_to_int(char: str) -> int:
            if char in "Xx":
                return 10
            return int(char)

        weighted_sum = sum((10 - i) * char_to_int(x) for i, x in enumerate(chars))

        if weighted_sum % 11 != 0:
            raise ISBN10FormatError(
                value=value, message="ISBN-10 weighted sum must be divisible by 11."
            )
        return value

    class Config:
        """Pydantic config class."""

        allow_mutation = False
        # anystr_lower = True


def main() -> None:
    """Main function."""
    # Read the data from the file
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        books: List[Book] = [Book(**item) for item in data]
        print(books[0].author)
        print(books[0].dict(include={"title", "author"}))
        print(books[0].dict(exclude={"title", "author"}))


if __name__ == "__main__":
    main()
