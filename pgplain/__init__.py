

from plasTeX.Renderers.Text import Renderer as BaseRenderer
import textwrap, re, string

class FancyWrapper(textwrap.TextWrapper):
    """Improved version of the textwrap library"""

    wordsep_simple_re = re.compile(r'( +)')
    wordsep_re = re.compile(
        r'( +|'                                  # any whitespace
        r'[^ \w]*\w+[^0-9\W]-(?=\w+[^0-9\W])|'   # hyphenated words
        r'(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w))')   # em-dash

    def __init__(self, **kwargs):
        textwrap.TextWrapper.__init__(self, drop_whitespace=False, **kwargs)

#        ulpat = u'\u02cd?[^ \u02cd]*[^ \u02cd\u201e]\u02cd'
        ulpat = u'\u02cd?[^ \u02cd]+\u02cd[,\\.;\\?]*'

        self.wordsep_re_uni = re.compile(u'( +|' + ulpat + r')', re.U)
        self.wordsep_simple_re_uni = re.compile(
            r'( +|'                                  # any whitespace
            + ulpat +
            r'[^ \w]*\w+[^0-9\W]-(?=\w+[^0-9\W])|'   # hyphenated words
            r'(?<=[\w\!\"\'\&\.\,\?])-{2,}(?=\w))'   # em-dash
            , re.U)

    def _indent(self, line):
        return self.subsequent_indent + ''.join(line)

    def _wrap_chunks(self, chunks):
        """_wrap_chunks(chunks : [string]) -> [string]

        Wrap a sequence of text chunks and return a list of lines of
        length 'self.width' or less.  (If 'break_long_words' is false,
        some lines may be longer than this.)  Chunks correspond roughly
        to words and the whitespace between them: each chunk is
        indivisible (modulo 'break_long_words'), but a line break can
        come between any two chunks.  Chunks should not have internal
        whitespace; ie. a chunk is either all whitespace or a "word".
        Whitespace chunks will be removed from the beginning and end of
        lines, but apart from that whitespace is preserved.
        """
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)

        # Arrange in reverse order so items can be efficiently popped
        # from a stack of chucks.
        chunks.reverse()
        last_len = 0

        while chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len is just the length of all the chunks in cur_line.
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - len(indent)

            # First chunk on line is whitespace -- drop it, unless this
            # is the very beginning of the text (ie. no lines started yet).
            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = len(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)
            # Balance line lengths -- better would be to review even older lines
            elif chunks and last_len != 0:
                l = len(lines[-1][-1])
                while last_len - l > cur_len + 1:
                    cur_line = [lines[-1][-1]] + cur_line
                    del lines[-1][-1]
                    cur_len +=l
                    last_len -= l
                    l = len(lines[-1][-1])


            if cur_line:
                lines.append(cur_line)
                last_len = cur_len

        if lines == []:
            return []

        for line in lines:
            while line and line[0].isspace():
                del line[0]
            while line and line[-1].isspace():
                del line[-1]
            if line and line[0].count(u'\u02cd') == 1:
                line[0] = u'\u02cd' + line[0]

        return ([self.initial_indent + ''.join(lines[0])] + 
            map(self._indent, lines[1:]))

#    def wrap(self, text):
#        return textwrap.TextWrapper.wrap(self, text.lstrip())

class pgtextRenderer(BaseRenderer):
    """ Renderer for plain text documents for upload to Project Gutenberg"""

    outputType = unicode
    fileExtension = '.utf8'
    lineWidth = 72
    underlinesym = u'\u02cd'   # Makron
    
    def __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)
        
        # Load dictionary with methods
#       Right now broken FIXME,TODO 
	self.Footnotes = []

    def unify_math_spaces(self, s):
        s = re.sub(u' \u00b7', u'\u00b7', s)
        return re.sub(r'(\S)=', r'\1 =', s)

    def processFileContent(self, document, s):
        # Put block level elements back in
        block_re = re.compile('(\\s*)\001\\[(\\d+)@+\\]')
        while 1:
            m = block_re.search(s)
            if not m:
                break

            space = ''
            before = m.group(1)
            if before is None:
                before = ''
            if '\n' in before:
                spaces = before.split('\n')
                space = spaces.pop()
                before = '\n'.join(spaces) + '\n'

            block = self.blocks[int(m.group(2))]
            block = space + block.replace('\n', u'\n%s' % space) 

            s = block_re.sub('%s%s' % (before, block), s, 1)

        # Clean up newlines
        #return re.sub(r'\s*\n\s*\n(\s*\n)+', r'\n\n\n', s)
        return s
    
    def postProcessText(self, s):
        #return re.sub(self.underlinesym+'+', '_', s)
        return re.sub(u'\u02cd+', '_', s)

    def wrap(self, s, **kwargs):
	w = FancyWrapper(width=self.lineWidth, break_long_words=False, **kwargs)
	return map(self.postProcessText, w.wrap(unicode(s)))
    
    def fill(self, s, **kwargs):
	w = FancyWrapper(width=self.lineWidth, break_long_words=False, **kwargs)
	return self.postProcessText(w.fill(unicode(s)))
    
    # Alignment

    # Arrays
    
    # Bibliography

    # Boxes
    
    # Breaking
    
    # Crossref
    
    # Floats
    
    # Font Selection
    
    # Footnotes
    def do_Footnote(self, node):
        mark = u'[%s]' % unicode(node.attributes['mark'])
        self.Footnotes.append(self.fill(node.attributes['text'],
                    initial_indent='%s ' % mark,
                    subsequent_indent=' ' * (len(mark)+1)).strip())
        return mark

    # Index
    
    # Lists

    # Math
    
    def do_math(self, node):
        # Remove _ before simple Numbers: x_3 -> x3
        s = re.sub(u'([^\u220f\u2210\u2211\u222b\u222e])_(\d)', r'\1\2',
            unicode(node))
        return re.sub(u' ', u'\u00a0', self.unify_math_spaces(s))

    do_ensuremath = do_math
    
    def do_equation(self, node):
        #s = u'   %s' % re.compile(r'^\s*\S+\s*(.*?)\s*\S+\s*$', re.S).sub(r'\1', node.source)
        #return re.sub(r'\s*(_|\^)\s*', r'\1', s)
        return self.center(self.do_math(node))

    do_displaymath = do_equation
    
    def do_eqnarray(self, node):
        def render(node):
            s = re.compile(r'^\$\\displaystyle\s*(.*?)\s*\$\s*$', re.S).sub(r'\1', node.source)
            return re.sub(r'\s*(_|\^)\s*', r'\1', s)
        s = self.do_array(node, cellspacing=(1,1), render=render)
        output = []
        for line in s.split('\n'):
            output.append('   %s' % line)
        return u'\n'.join(output)     

    do_align = do_gather = do_falign = do_multiline = do_eqnarray 
    do_multline = do_alignat = do_split = do_eqnarray
    
    # Misc
    
    # Pictures
    
    # Primitives
    
    def do_par(self, node):
        numchildren = len(node.childNodes)
        if numchildren == 1 and not isinstance(node[0], basestring):
            return u'%s\n\n' % unicode(node)
        elif numchildren == 2 and isinstance(node[1], basestring) and \
           not node[1].strip():
            return u'%s\n\n' % unicode(node)
        s = u'%s\n\n' % self.fill(node)
	if self.Footnotes:
#	if Footnotes:
            Footnotes = u'\n\n'.join(self.Footnotes)
            self.Footnotes = []
            s = u'%s%s\n\n' % (s, Footnotes)
        if not s.strip():
            return u''
        return s

    def do__superscript(self, node):
        #return self.default(node)
        s = self.default(node)
        # Check for primes
        if s.startswith(u'\u2032'):
            return s
	return '^'+s

    # TODO: More special cases - like string lenght?
    def do__subscript(self, node):
        s = self.default(node)
        return '_'+s

    def do_mathrm(self, node):
        return self.default(node)
    
    # Quotations
    
    # Sectioning

    def do_maketitle(self, node):
        output = []
        metadata = node.ownerDocument.userdata
        if 'publishers' in metadata:
            output.append(self.center(metadata['publishers']).rstrip())
        if 'uppertitleback' in metadata or 'lowertitleback' in metadata:
            output.append(u'\n\n')
        if 'uppertitleback' in metadata:
            output.append(self.fill(unicode(metadata['uppertitleback'])))
        if 'lowertitleback' in metadata:
            output.append(u'\n%s' % self.fill(unicode(metadata['lowertitleback'])))
        if 'dedication' in metadata:
            output.append(u'\n\n\n')
            output.append(self.center(metadata['dedication']).rstrip())
        return BaseRenderer.do_maketitle(self, node) + u'\n'.join(output)
#        return u'\n%s\n\n' % u'\n'.join(output)

# Workaround: Hardcode disabling of autogenerated numbering
    def do_section(self, node):
        return u'\n\n\n%s' % (u'%s\n\n%s' % (self.fill(node.title), node)).strip()

    do_subsection = do_subsubsection = do_section
    do_paragraph = do_subparagraph = do_subsubparagraph = do_section

# Workaround: Hardcode disabling of autogenerated numbering
    def do_chapter(self, node):
        return u'\n\n\n\n\n%s' % (u'%s\n\n\n%s' % (self.fill(node.title), node)).strip()

    do_part = do_chapter

    do_dedication = do_publishers = do_uppertitleback = do_lowertitleback = BaseRenderer.do_title
    
    # Sentences

    def do_spacedout(self, node):
        return re.sub(r'(\S)', r'\1'+u'\u202f', re.sub(r'(\s)', r'\1 ', self.default(node)))
    
    def do_underline(self, node):
        #return u'_%s_' % re.sub(r'\s', r'_', self.default(node))
        #return u'_%s_' % self.default(node)
        return (self.underlinesym + 
            re.sub(r'\s', self.underlinesym, self.default(node)) +
            self.underlinesym)

    do_em = do_emph = do_underline

    # Space
    
    # Tabbing - not implemented yet
    
    # Verbatim
    
    def do_marginline(self, node):
        return u''

Renderer = pgtextRenderer
