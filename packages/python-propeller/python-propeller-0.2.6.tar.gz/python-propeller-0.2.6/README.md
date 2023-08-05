python-propeller
================

Pretty progress and load indicators.

Installation:

    pip install python-propeller

    $ python
    >>> from propeller import demo, propeller
    >>> demo()

Usage as spinner:

    with propeller("spinning propeller") as p:
        # do something
        p.spin()

        # do more
        p.spin()

        # print to console
        p.println("without messing up the spinner")

        # replace "spinning propeller"
        p.msg("spinner")

        ...


Usage with progress indicator:

    with propeller("progress propeller") as p:
        n = 1000
        for i in range(n):
            # do something
            p.progress(i, n)


Process a collections:

    def preprocessor(item):
        # preprocess

    def finalizer(item):
        # finalize

    pre_processed = propeller("preprocessing").map(preprocess, in_list)
    propeller("finalizing").process(finalizer, pre_processed)


If the length of your collections can be determined, a progress bar will be
displayed. If iterables are given, a spinner will be displayed. If you know
the size of your iterables, you can explicitly specify it with the `n`
keyword argument:

    def doit(item):
        # work

    propeller().process(doit, a_iterable, b_iterable, n=42)


`python-propeller` uses threading and needs to be ended cleanly. This can be
done by using `process`, `map` or `imap` functions, using the `with` statement
or explicitly calling the `end` method when you are finished.

    p = propeller()
    try:
        # do something
    finally:
        p.end()


Various measurements are optional:

    with propeller(eta=False, ops=False, eta=False, percent=False) as plain_p:
        plain_p.spin()


Customization
-------------

The classic propeller can be made like so:

    from time import sleep

    def noop(item):
        sleep(0.01)

    propeller(spinner="|/-\\").process(noop, iter(range(300)))


But this is also one of the many preconfigured styles:

    propeller(spinner='lines').process(noop, iter(range(300)))


With progress bars the first character of the string is used for the unfilled
portion of the bar and the last character for the filled portion:

    propeller(bar=' -+=').process(noop, range(300))

    # produces something like this:
    ========-                                 [ops: 99][eta: 2s][23%]


Included styles for both spinners and progress bars:

    `shades`        ┄░▒▓█ (default)
    `hbar`          ▁▂▃▄▅▆▇█
    `vbar`           ▏▎▍▌▋▊▉█
    `dots`          ⠀⠁⠃⠇⡇⣇⣧⣷⣿

    # print all spinner and progress bar styles
    from propeller import print_styles
    print_styles()
