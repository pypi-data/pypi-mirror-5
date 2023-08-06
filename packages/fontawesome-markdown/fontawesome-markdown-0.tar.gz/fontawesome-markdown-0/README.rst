FontAwesome and Markdown, together!
-----------------------------------

A Markdown extension that looks for things like ``:icon-coffee:`` and replaces them with the FontAwesome icon markup.

Add a `FontAwesomeExtension` instance to your Markdown call and watch the magic unfold::

    >>> from markdown import Markdown
    >>> from fontawesome_markdown import FontAwesomeExtension

    >>> markdown = Markdown(extensions=[FontAwesomeExtension()]
    >>> markdown.convert('i ♥ :icon-coffee:')
    <p>i ♥ <i class="icon icon-coffee"></i></p>

Don't forget to make the FontAwesome assets available to your DOM!
