from dexy.exceptions import UserFeedback
from dexy.doc import Doc
from tests.utils import wrap
from nose.tools import raises
import os

def test_output_name_with_filters():
    with wrap() as wrapper:
        doc = Doc(
                "data.md|markdown",
                wrapper,
                [],
                output_name="finished.bar",
                contents="foo"
                )
        wrapper.run_docs(doc)

        assert doc.initial_data.name == "data.md"
        assert doc.output_data().output_name() == "finished.bar"

def test_custom_name():
    with wrap() as wrapper:
        doc = Doc(
                "data.txt",
                wrapper,
                [],
                output_name="data.abc",
                contents="12345.67"
                )
        wrapper.run_docs(doc)

        assert doc.output_data().output_name() == "data.abc"

def test_custom_name_in_subdir():
    with wrap() as wrapper:
        doc = Doc(
                "data.txt",
                wrapper,
                [],
                output_name="subdir/data.abc",
                contents="12345.67"
                )
        wrapper.run_docs(doc)
        wrapper.report()

        assert doc.output_data().output_name() == "subdir/data.abc"
        assert doc.output_data().parent_output_dir() == "subdir"

def test_custom_name_with_args():
    with wrap() as wrapper:
        doc = Doc(
                "data.txt",
                wrapper,
                [],
                output_name="%(bar)s/data-%(foo)s.abc",
                foo='bar',
                bar='baz',
                contents="12345.67"
                )
        wrapper.run_docs(doc)
        wrapper.report()

        assert doc.output_data().output_name() == "baz/data-bar.abc"
        assert doc.output_data().parent_output_dir() == "baz"
        assert os.path.exists("output/baz/data-bar.abc")

@raises(UserFeedback)
def test_custom_name_with_evil_args():
    with wrap() as wrapper:
        doc = Doc(
                "data.txt",
                wrapper,
                [],
                output_name="/%(bar)s/data-%(foo)s.abc",
                foo='bar',
                bar='baz',
                contents="12345.67"
                )
        wrapper.run_docs(doc)
