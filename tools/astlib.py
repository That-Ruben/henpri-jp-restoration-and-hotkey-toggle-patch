"""Parser for Artemis .ast scenario scripts (Lua-table subset).

The files are machine-generated: `astver = 2.0\nast = { ... }` where the
table uses only string/number/boolean values, ["quoted"] or bare-name keys,
and nested tables. We parse that subset into Python structures.

A parsed table is a `LuaTable` holding `array` (positional values) and
`hash` (key -> value), preserving enough to re-serialize losslessly for our
purposes (we re-emit in the same generated style).
"""


class LuaTable:
    __slots__ = ("array", "hash", "order")

    def __init__(self):
        self.array = []
        self.hash = {}
        self.order = []  # (kind, key_or_index) in source order, kind in {"a","h"}

    def items_in_order(self):
        for kind, k in self.order:
            if kind == "a":
                yield None, self.array[k]
            else:
                yield k, self.hash[k]

    def __repr__(self):
        return f"LuaTable(array={len(self.array)}, hash={list(self.hash)[:4]})"


class Parser:
    def __init__(self, text):
        self.s = text
        self.i = 0
        self.n = len(text)
        self.keystack = []
        self.span_hook = None  # fn(keystack_tuple, start, end) for hash values

    def error(self, msg):
        line = self.s.count("\n", 0, self.i) + 1
        raise ValueError(f"parse error line {line}: {msg}")

    def skip_ws(self):
        s, n = self.s, self.n
        while self.i < n:
            c = s[self.i]
            if c in " \t\r\n":
                self.i += 1
            elif s.startswith("--", self.i):
                j = s.find("\n", self.i)
                self.i = n if j < 0 else j + 1
            else:
                break

    def peek(self):
        return self.s[self.i] if self.i < self.n else ""

    def expect(self, ch):
        if self.peek() != ch:
            self.error(f"expected {ch!r}, got {self.peek()!r}")
        self.i += 1

    def parse_string(self):
        quote = self.s[self.i]
        self.i += 1
        out = []
        s = self.s
        while True:
            c = s[self.i]
            if c == "\\":
                out.append(s[self.i : self.i + 2])
                self.i += 2
            elif c == quote:
                self.i += 1
                return "".join(out)
            else:
                out.append(c)
                self.i += 1

    def _parse_hash_value(self, key):
        self.keystack.append(key)
        self.skip_ws()
        start = self.i
        val = self.parse_value()
        if self.span_hook:
            self.span_hook(self.keystack, start, self.i)
        self.keystack.pop()
        return val

    def parse_longstring(self):
        # [[...]] Lua long string, no escapes
        end = self.s.find("]]", self.i + 2)
        if end < 0:
            self.error("unterminated long string")
        content = self.s[self.i + 2 : end]
        self.i = end + 2
        return ("longstr", content)

    def parse_value(self):
        self.skip_ws()
        c = self.peek()
        if c == "{":
            return self.parse_table()
        if c in "\"'":
            return self.parse_string()
        if c == "[" and self.s.startswith("[[", self.i):
            return self.parse_longstring()
        # bare token: number / true / false / identifier
        j = self.i
        s = self.s
        while j < self.n and (s[j].isalnum() or s[j] in "._-+"):
            j += 1
        tok = s[self.i : j]
        if not tok:
            self.error("empty value")
        self.i = j
        if tok == "true":
            return True
        if tok == "false":
            return False
        try:
            return int(tok)
        except ValueError:
            pass
        try:
            return float(tok)
        except ValueError:
            pass
        return ("ident", tok)

    def parse_table(self):
        self.expect("{")
        t = LuaTable()
        while True:
            self.skip_ws()
            c = self.peek()
            if c == "}":
                self.i += 1
                return t
            if c == "[" and self.s.startswith("[[", self.i):
                val = self.parse_longstring()
                t.array.append(val)
                t.order.append(("a", len(t.array) - 1))
            elif c == "[":
                self.i += 1
                self.skip_ws()
                if self.peek() in "\"'":
                    key = self.parse_string()
                else:
                    key = self.parse_value()
                self.skip_ws()
                self.expect("]")
                self.skip_ws()
                self.expect("=")
                val = self._parse_hash_value(key)
                t.hash[key] = val
                t.order.append(("h", key))
            elif c in "\"'":
                # could be a positional string; strings are never keys unbracketed
                val = self.parse_string()
                t.array.append(val)
                t.order.append(("a", len(t.array) - 1))
            elif c == "{":
                val = self.parse_table()
                t.array.append(val)
                t.order.append(("a", len(t.array) - 1))
            else:
                # bare word: either `name=value` or a positional bare value
                j = self.i
                s = self.s
                while j < self.n and (s[j].isalnum() or s[j] in "._-+"):
                    j += 1
                save = self.i
                self.i = j
                self.skip_ws()
                if self.peek() == "=":
                    self.i += 1
                    key = s[save:j]
                    val = self._parse_hash_value(key)
                    t.hash[key] = val
                    t.order.append(("h", key))
                else:
                    self.i = save
                    val = self.parse_value()
                    t.array.append(val)
                    t.order.append(("a", len(t.array) - 1))
            self.skip_ws()
            if self.peek() == ",":
                self.i += 1


def parse_ast_file(path):
    """Returns (astver_line, ast LuaTable, trailing_text)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    idx = text.find("ast = {")
    if idx < 0:
        idx = text.find("ast={")
        brace = text.find("{", idx)
    else:
        brace = text.find("{", idx)
    header = text[:brace]
    p = Parser(text)
    p.i = brace
    table = p.parse_table()
    trailing = text[p.i :]
    return header, table, trailing


PLACEHOLDER = "*テキスト*"


def block_text_summary(block):
    """For a label block LuaTable, return dict lang -> list of page line-counts,
    or None if the block has no text table."""
    tx = block.hash.get("text")
    if not isinstance(tx, LuaTable):
        return None
    out = {}
    for lang, pages in tx.hash.items():
        if not isinstance(pages, LuaTable):
            continue
        counts = []
        for page in pages.array:
            if isinstance(page, LuaTable):
                # strings in page.array are display lines; tables are inline cmds
                lines = [x for x in page.array if isinstance(x, str)]
                counts.append(len(lines))
        out[lang] = counts
    return out
