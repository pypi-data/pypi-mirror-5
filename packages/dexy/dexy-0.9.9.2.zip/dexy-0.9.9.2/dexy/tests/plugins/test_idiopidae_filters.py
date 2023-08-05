from dexy.doc import Doc
from dexy.tests.utils import wrap

def test_idio_invalid_input():
    with wrap() as wrapper:
        wrapper.debug = False
        doc = Doc("hello.py|idio",
                wrapper, [],
                contents=" ")
        wrapper.run_docs(doc)
        assert wrapper.state == 'error'

def test_idio_bad_file_extension():
    with wrap() as wrapper:
        wrapper.debug = False
        doc = Doc("hello.xyz|idio", wrapper, [], contents=" ")
        wrapper.run_docs(doc)
        assert wrapper.state == 'error'

def test_multiple_sections():
    with wrap() as wrapper:
        src = """
### @export "vars"
x = 6
y = 7

### @export "multiply"
x*y

"""
        doc = Doc("example.py|idio",
                wrapper,
                [],
                contents=src)

        wrapper.run_docs(doc)

        assert doc.output_data().keys() == ['1', 'vars', 'multiply']

def test_force_text():
    with wrap() as wrapper:
        node = Doc("example.py|idio|t",
                wrapper,
                [],
                contents="print 'hello'\n")

        wrapper.run_docs(node)
        assert str(node.output_data()) == "print 'hello'\n"

def test_force_latex():
    with wrap() as wrapper:
        doc = Doc("example.py|idio|l",
                wrapper,
                [],
                contents="print 'hello'\n")

        wrapper.run_docs(doc)

        assert "begin{Verbatim}" in str(doc.output_data())
