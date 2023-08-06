"""
Module to assist in the super-common operation of
wrapping values with prefix and suffix strings.
"""

import re
import six
from options import Options, Prohibited, Transient


def is_string(v):
    return isinstance(v, six.string_types)


def stringify(v):
    """
    Return a string. If it's already a string, just return that.
    Otherwise, stringify it. Not safe for Python 3.
    """
    return v if is_string(v) else str(v)


class BadStyleName(ValueError):
    pass


class Quoter(object):
    """
    A quote style. Instantiate it with the style information. Call
    it with a value to quote the value.
    """

    styles = {}         # remember named styles
                        # NB global across all style Quoter classes

    options = Options(
        prefix       = None,
        suffix       = None,
        name         = None,
        margin       = 0,
        padding      = 0,
        encoding     = None,
        style        = None,
    )


    def __init__(self, *args, **kwargs):
        """
        Create a quoting style.
        """
        opts = self.options = self.__class__.options.push(kwargs)
        self._flatargs(args)
        self._register_name(opts.name)

    def _flatargs(self, args):
        """
        Consume 'flat' *args if present when object is constructed.
        """
        if args:
            opts = self.options
            used = opts.addflat(args, ['prefix', 'suffix'])
            if 'suffix' not in used:
                opts.suffix = opts.prefix
                # this suffix = prefix behavior appropriate for flat args only

    def _register_name(self, name, cls=None):
        """
        Given a name or space-separated list of names, define styles
        based on that name, and define class attributes for that style
        name as well (as long as such a style name doesn't start with
        an underscore, which is hereby prohibuted for style names to
        avoid conflict with existing Quoter methods.)
        """
        if not name:
            return
        cls = cls or self.__class__
        if ' ' in name:
            names = name.split()
            self.options.name = name.replace(' ', '-')
        else:
            names = [name]
        for n in names:
            if not n.startswith('_'):
                Quoter.styles[n] = self
                setattr(Quoter, n, self)
            else:
                msg = 'Style names should not start with an underscore'
                raise BadStyleName(msg)

    def _whitespace(self, opts):
        """
        Compute the appropriate margin and padding strings.
        """
        pstr = ' ' * opts.padding if isinstance(opts.padding, int) else opts.padding
        mstr = ' ' * opts.margin  if isinstance(opts.margin, int)  else opts.margin
        return (pstr, mstr)

    def _output(self, parts, opts):
        """
        Given a list of string parts, concatentate them and output
        with the given encoding (if any).
        """
        outstr = ''.join(parts)
        return outstr.encode(opts.encoding) if opts.encoding else outstr

    def __call__(self, value, **kwargs):
        """
        Quote the value, with the given padding, margin, and encoding.
        """
        opts = self.options.push(kwargs)
        if opts.style:
            return Quoter.styles[opts.style](value, **kwargs)
        else:
            pstr, mstr = self._whitespace(opts)
            suffix = opts.suffix if opts.suffix is not None else opts.prefix
            parts = [ mstr, opts.prefix, pstr, stringify(value), pstr, suffix, mstr ]
            return self._output(parts, opts)

# create some default named styles (ASCII)

quote    = Quoter("'",      name= 'default')

braces   = Quoter('{', '}', name='braces')
brackets = Quoter('[', ']', name='brackets')
angles   = Quoter('<', '>', name='angles')
parens   = Quoter('(', ')', name='parens')
qs = single   = Quoter("'",      name='single qs')
qd = double   = Quoter('"',      name='double qd')
qt = triple   = Quoter('"""',    name='triple qt')
qb = backticks= Quoter("`",      name='backticks qb')

# and some Unicode styles
anglequote = guillemet = Quoter(six.u('\u00ab'), six.u('\u00bb'), name='anglequote guillemet')
curlysingle = Quoter(six.u('\u2018'), six.u('\u2019'), name='curlysingle')
curlydouble = Quoter(six.u('\u201c'), six.u('\u201d'), name='curlydouble')


class LambdaQuoter(Quoter):

    """
    A Quoter that uses code to decide what quotes to use, based on the value.
    """

    options = Quoter.options.add(
        func   = None,
        prefix = Prohibited,
        suffix = Prohibited,
    )

    def _flatargs(self, args):
        """
        Consume 'flat' *args if present when object is constructed.
        """
        if args:
            self.options.addflat(args, ['func'])

    def __call__(self, value, **kwargs):
        """
        Quote the value, based on the instance's function.
        """
        opts = self.options.push(kwargs)
        if opts.style:
            return Quoter.styles[opts.style](value, **kwargs)
        else:
            pstr, mstr = self._whitespace(opts)
            prefix, value, suffix = opts.func(value)
            parts = [mstr, prefix, pstr, stringify(value), pstr, suffix, mstr]
            return self._output(parts, opts)


class XMLQuoter(Quoter):

    """
    A more sophisticated quoter for XML elements that manages tags,
    namespaces, and the idea that some elements may not have contents.
    """

    options = Quoter.options.add(
        tag      = None,
        ns       = None,
        atts     = {},
        attquote = single,
        void     = False,
        prefix   = Prohibited,
        suffix   = Prohibited,
    )

    def __init__(self, *args, **kwargs):
        """
        Create an XMLQuoter
        """
        # Restating basic init to avoid errors of self.__getattr__
        opts = self.options = self.__class__.options.push(kwargs)
        self._flatargs(args)
        self._register_name(opts.name)

        create_atts = opts.atts
        opts.tag, opts.atts = self._parse_selector(opts.tag)
        if create_atts:
            opts.atts.update(create_atts)
        # explicit addition of atts

        # NB this is an explicit multi-setter

    def _flatargs(self, args):
        """
        Consume 'flat' *args if present when object is constructed.
        """
        if args:
            self.options.addflat(args, ['tag', 'atts'])

    def __getattr__(self, name):
        try:
            return XMLQuoter.__dict__[name]
        except KeyError:
            return XMLQuoter(name, name=name)

    def _attstr(self, atts, opts):
        """
        Format an attribute dict.
        """
        return ' '.join([''] + ["{0}={1}".format(k, opts.attquote(v)) for k,v in atts.items()])

    def _parse_selector(self, selector):
        """
        Parse a selector (modeled on jQuery and CSS). Returns a (tagname, id, classes)
        tuple.
        """
        tagnames = re.findall(r'^(\w+)',      selector)
        classes  = re.findall(r'\.([\w\-]+)', selector)
        ids      = re.findall(r'\#([\w\-]+)', selector)
        assert len(tagnames) <= 1
        assert len(ids) <= 1
        atts = {}
        if ids:
            atts['id'] = ids[0]
        if classes:
            atts['class'] = ' '.join(classes)
        return (tagnames[0] if tagnames else None, atts)

    def __call__(self, *args, **kwargs):
        """
        Quote a value in X/HTML style, with optional attributes.
        """

        if 'style' in kwargs:
            stylename = kwargs['style']
            del kwargs['style']
            return Quoter.styles[stylename](*args, **kwargs)
        else:

            if 'atts' in kwargs:
                catts = kwargs['atts']
                del kwargs['atts']
            else:
                catts = {}

            value = ''
            if len(args) > 0:
                value = args[0]
            if len(args) > 1:
                catts = args[1]
            if len(args) > 2:
                raise ValueError('just one or two args, please')

            opts = self.options.push(kwargs)
            pstr, mstr = self._whitespace(opts)

            # do we need some special processing to remove atts from the kwargs?
            # or some magic to integrate call atts to with existing atts?
            # or ..?
            # this is a good test / hard case for the magial processing
            # probably magic

            callatts = self._parse_selector(catts)[1] if is_string(catts) else catts
            atts = {}
            atts.update(opts.atts)
            atts.update(callatts)

            astr = self._attstr(atts, opts) if atts else ''
            ns = opts.ns + ':' if opts.ns else ''
            if opts.void or not args:
                parts = [ mstr, '<', ns, opts.tag, astr, '>', mstr ]
            else:
                parts = [ mstr, '<', ns, opts.tag, astr, '>', pstr,
                          stringify(value),
                          pstr, '</', ns, opts.tag, '>', mstr ]
            return self._output(parts, opts)

    # could improve kwargs handling of HTMLQuoter

    # question is, should call attributes overwrite, or add to, object atts?
    # may not be a single answer - eg, in case of class especially

    # This might be case where replace is the primary option, but there's
    # an option to add (or even subtract) - say using a class Add, Plus, Subtract,
    # Minus, Relative, Rel, Delta, etc as an indicator

    # To be a full production XML quoter, might need a slightly more robust
    # way to name XML styles that include namespace names, rather than the
    # simpler scheme here. When a tag is auto-instantiated, it could
    # perhaps have its ns defined as part of its definition, like tag is.


class HTMLQuoter(XMLQuoter):

    """
    A more sophisticated quoter that supports attributes and void elements for HTML.
    """

    options = XMLQuoter.options.add(
        ns       = Prohibited,
    )

    def __getattr__(self, name):
        try:
            return HTMLQuoter.__dict__[name]
        except KeyError:
            return HTMLQuoter(name, name=name)

_ml_quoter = Quoter(prefix='<!--', suffix='-->')

html = HTMLQuoter('html')
setattr(HTMLQuoter, 'comment', _ml_quoter)
# HTML comments are normal quoters, not tag-based

xml = XMLQuoter('xml')
setattr(XMLQuoter, 'comment', _ml_quoter)


# Eventually working way toward a CSS box model style formatting in which there
# can be a marginleft, marginright, paddingleft, and paddingright (i.e.
# separating left and right magin/padding specs). It might even be possible
# to provide borders (top and bottom), and to reconsider prefix and suffix
# as left and right borders. Alignment of content within a cell and various
# forms of multi-line justification might also be feasible.
