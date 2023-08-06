# htmlol

htmlol is an HTML5-compliant structured HTML construction library for Python 3.  
It is used for building an HTML document and outputting it in plain text.

All valid HTML5 elements are provided in the `htmlol` namespace.

### Introduction

Constructing a simple, minimally correct HTML5 document and writing to stdout:

    import htmlol as h

    doc = h.Document(
        h.meta(charset = 'utf-8'),
        h.title('Title'),
        'Hello, world!'
    )

    print(doc)

Generates the following HTML *(newlines added for clarity)*:

    <!DOCTYPE html>
    <meta charset="utf-8">
    <title>Title</title>
    Hello, world!

Attributes can be added as keywords.  
Reserved words must be prefixed with a single underscore (`_`).

    p = h.p(
        h.a('Visit my blog!', href = '/blog'),
        _class = 'content'
    )

    print(p)

Standard attribute prefixes such as `data-` and `xmlns:` are also supported
by substituting an underscore (`_`) for characters `-` or `:`.

    p = h.p(
        'Blah blah blah',
        data_my_data_attribute = 'somedata',
        xmlns_lang = 'en'
    )

    print(p)

Some attributes take boolean values. These will be rendered in abbreviated form
if `True` is given and omitted if `False` is given.

    div = h.div(
        h.button(
            'Click me!',
            type = 'button',
            disabled = False
        ),
        h.button(
            "Don't click me!",
            type = 'button',
            disabled = True
        )
    )

    print(div)

Any iterable object containing text or HTML elements, such as a list or generator,
can be used to initialize a new element object.

    ul = h.ul(
        h.li(user.name)
            for user in users
    )

    print(ul)

Here's a full document containing some of the previous examples:

    import htmlol as h

    doc = h.Document(
        h.head(
            h.meta(charset = 'utf-8'),
            h.title('Title')
        ),

        h.body(
            h.div(
                h.p('Welcome to my ', h.b('awesome'), ' website!'),

                h.p(h.a('You can also visit my blog!', href = '/blog')),

                h.p(
                    h.div('Look at some of these pages:'),

                    (h.p(h.a(p.title, href = p.url))
                        for p in pages)
                ),

                _class = 'content'
            )
        )
    )

    print(doc)
