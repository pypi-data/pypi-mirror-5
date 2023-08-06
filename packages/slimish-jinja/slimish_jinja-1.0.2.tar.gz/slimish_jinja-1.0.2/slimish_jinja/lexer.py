import re
from .tokens import *

class Lexer(object):
    """
    Tokenizes slim templates.
    """

    key_val_pat = re.compile(r'\s+ ([^\s]+?) \s*=\s* (["\']) ([^\2]*?) \2', re.X)
    whitespace = re.compile(r'\s+')

    def __init__(self, src):
        self.__dict__.update(src=src, indents=[], in_text_block=False,
                             buf=[], lineno=0)
        self.handlers = {'-': self.handle_jinja,
                         '{': self.handle_jinja_output,
                         '|': self.handle_text,
                         '%': self.handle_empty_html,
                         '@': self.handle_empty_jinja,
                         '!': self.handle_doctype}

    def join_src_lines(self):
        src_iter = iter(self.src)
        lines = []
        while True:
            line = next(src_iter)
            if line.rstrip().endswith('\\'):
                lines.append(line.rstrip()[:-1])
            else:
                if lines:
                    lines.append(line.strip())
                    yield ' '.join(lines)
                    lines = []
                else:
                    yield line


    def __call__(self):
        """
        Tokenizes `self.src` and yields `Token` objects..
        """
        for line in self.join_src_lines():
            self.lineno += 1
            # Ignore blank lines and comments.
            stripped_line = line.strip()
            if not stripped_line or (stripped_line and stripped_line[0] == '/'):
                continue
            # Check for indent changes.
            indent_change = self.check_indent(line)
            if indent_change:
                change_type, indent_change = indent_change
                if self.in_text_block and change_type == UNINDENT:
                    yield TextToken(TEXT, self.lineno, '\n'.join(self.buf))
                    self.in_text_block = False
                    self.buf = []
                for change in indent_change:
                    yield change
            # Keep reading text if we are in text block.
            if self.in_text_block:
                self.buf.append(line[self.indents[-1]:].rstrip())
                continue
            # Pass the read line to relevant handler.
            first_char = stripped_line[0]
            handler = self.handlers.get(first_char, self.handle_html)
            ret = handler(stripped_line)
            if ret: yield ret

        # yield pending text block.
        if self.buf:
            yield TextToken(TEXT, self.lineno, '\n'.join(self.buf))
        # yield implicity closed tags.
        indents = self.indents
        lineno = self.lineno
        while indents:
            yield IndentToken(UNINDENT, lineno, ' ' * indents.pop())
            lineno += 1
        # unindent for `html` for which no indent was recorded.
        yield IndentToken(UNINDENT, lineno, '')

    def check_indent(self, line):
        """
        Checks for increase or decrease in indent.
        yields `IndentToken` if index changes.
        """
        current_indent = self.whitespace.match(line)
        indent_len = 0
        if current_indent:
            current_indent = current_indent.group()
            indent_len = len(current_indent)
        indents = self.indents
        # Record indents.
        if (not indents and current_indent) or (indents and indent_len > indents[-1]):
            # Indents are part of text if in text block.
            if not self.in_text_block:
                indents.append(indent_len)
                return INDENT, [IndentToken(INDENT, self.lineno, current_indent)]
        elif indents and indent_len < indents[-1]:
            changes = []
            while indents and indents[-1] > indent_len:
                changes.append(IndentToken(UNINDENT, self.lineno, ' ' * indents.pop()))
            return UNINDENT, changes
        return False

    def extract_values(self, tag_name, line):
        """
        Extracts `key=val` pairs and `contents` from the given `tokens`
        and returns the resulting dictionary and contents.
        """
        attrs = {}
        contents = ''
        # Get the attributes for the tag.
        m = None
        for m in self.key_val_pat.finditer(line):
            attrs[m.group(1)] = m.group(3)
        if not m or m.end() < len(line) - 1:
            start_idx = m.end() if m else len(tag_name)
            contents = line[start_idx + 1:]
        return attrs, contents

    def handle_html(self, line):
        """
        Returns token for html tags.
        """
        tag_and_vals = self.whitespace.split(line)
        tag_name = tag_and_vals[0]
        tag_name_without_class_and_id = tag_name.split('#')[0].split('.')[0]

        # Get the attributes for the tag.
        attrs, contents = self.extract_values(tag_name, line)
        if contents:
            return HtmlToken(HTML_TAG, self.lineno, tag_name, attrs, contents)
        elif tag_name_without_class_and_id in HtmlToken.no_content_html_tags:
            return HtmlToken(HTML_NC_TAG, self.lineno, tag_name, attrs)
        else:
            return HtmlToken(HTML_TAG_OPEN, self.lineno, tag_name, attrs)

    def handle_empty_html(self, line):
        """
        Returns token for empty html elements.
        %div => <div></div>
        """
        tag_and_vals = self.whitespace.split(line[1:])
        tag_name = tag_and_vals[0]
        # Get the attributes for the tag.
        attrs, _ = self.extract_values(tag_name, line)
        return HtmlToken(HTML_TAG, self.lineno, tag_name, attrs, contents=' ')

    def handle_jinja(self, line):
        """
        Handles jinja tags.
        """
        parts = self.whitespace.split(line)
        if parts[0] == '-':
            tag_name = parts[1]
        else:
            tag_name = parts[0][1:]
        contents = line[1:].lstrip()
        if tag_name in JinjaToken.no_content_jinja_tags:
            return JinjaToken(JINJA_NC_TAG, self.lineno, tag_name, contents)
        return JinjaToken(JINJA_OPEN_TAG, self.lineno, tag_name, contents)

    def handle_empty_jinja(self, line):
        """
        Handles empty jinja tags.
        @block title => {% block title %}{% endblock %}
        """
        tag_name = self.whitespace.split(line)[0][1:]
        return JinjaToken(JINJA_TAG, self.lineno, tag_name, line[1:])

    def handle_text(self, line):
        """
        Handles text nested with pipes.
        """
        self.in_text_block = True
        self.buf.append(line[1:])

    def handle_jinja_output(self, line):
        """
        Handles output statements
        """
        contents = line.lstrip()
        return JinjaOutputToken(JINJA_OUTPUT_TAG, self.lineno, contents)

    def handle_doctype(self, line):
        """
        Handles text nested with pipes.
        """
        return DoctypeToken(DOCTYPE, self.lineno, line)
