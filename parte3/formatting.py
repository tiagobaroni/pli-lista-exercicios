"""Console formatting utilities for Parte 3: numbers, tables, section headers."""

from __future__ import annotations


def format_number(value: float, decimals: int = 2) -> str:
    """Format a float using Brazilian decimal conventions (comma as separator).

    Parameters
    ----------
    value:
        The number to format.
    decimals:
        Decimal places.  0 → integer with no point; >0 → fixed decimal with comma.
    """
    if decimals == 0:
        return str(int(round(value)))
    return f"{value:.{decimals}f}".replace(".", ",")


def print_section(title: str) -> None:
    """Print a top-level section banner."""
    width = max(len(title) + 6, 60)
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_subsection(title: str) -> None:
    """Print a subsection header."""
    print(f"\n--- {title} ---")


def print_matrix(
    data: list[list[float]],
    row_labels: list[str],
    col_labels: list[str],
    title: str = "",
    decimals: int = 2,
) -> None:
    """Print a 2-D matrix with labelled rows and columns.

    Parameters
    ----------
    data:
        Rows of numeric values.
    row_labels:
        One label per row.
    col_labels:
        One label per column.
    title:
        Optional title printed above the matrix.
    decimals:
        Decimal places passed to format_number.
    """
    if title:
        print(f"\n{title}")

    n_cols = len(col_labels)

    col_widths: list[int] = []
    for j in range(n_cols):
        w = len(col_labels[j])
        for row in data:
            w = max(w, len(format_number(row[j], decimals)))
        col_widths.append(w)

    row_label_w = max(len(r) for r in row_labels)

    header_cells = "  ".join(c.rjust(col_widths[j]) for j, c in enumerate(col_labels))
    print(" " * (row_label_w + 2) + header_cells)
    print("-" * (row_label_w + 2 + len(header_cells)))

    for label, row in zip(row_labels, data):
        cells = "  ".join(
            format_number(max(0.0, v), decimals).rjust(col_widths[j])
            for j, v in enumerate(row)
        )
        print(f"{label.ljust(row_label_w)}  {cells}")
