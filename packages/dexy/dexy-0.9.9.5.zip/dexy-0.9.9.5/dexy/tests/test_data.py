from dexy.doc import Doc
from dexy.tests.utils import wrap
import dexy.data
import dexy.exceptions
import os

def test_canonical_name():
    with wrap() as wrapper:
        doc = Doc("hello.txt",
                wrapper,
                [],
                contents="hello",
                output_name="yello.abc")

        wrapper.run_docs(doc)
        assert doc.output_data().output_name() == "yello.abc"
        wrapper.report()
        assert os.path.exists(os.path.join('output', 'yello.abc'))

def test_attempt_write_outside_project_root():
    with wrap() as wrapper:
        try:
            doc = Doc("../../example.txt",
                wrapper,
                [],
                contents = "hello")
            doc.setup()
            doc.setup_datas()
            assert False, 'should raise UserFeedback'
        except dexy.exceptions.UserFeedback as e:
            print str(e)
            assert 'trying to write' in str(e)

def test_key_value_data():
    with wrap() as wrapper:
        settings = {
                'canonical-name' : 'doc.json',
                'storage-type' : 'json'
                }
        data = dexy.data.KeyValue("doc.json", ".json", "doc.json", settings, wrapper)
        data.setup_storage()

        assert not data._data
        assert data.storage._data == {}

        # We use the append method to add key-value pairs.
        data.append('foo', 'bar')
        assert len(data.keys()) == 1

        assert data.value('foo') == 'bar'
        assert data.storage['foo'] == 'bar'
        assert data.as_text() == "foo: bar"

def test_key_value_data_sqlite():
    with wrap() as wrapper:
        wrapper.to_walked()
        wrapper.to_checked()

        settings = {
                'canonical-name' : 'doc.sqlite3'
                }

        data = dexy.data.KeyValue("doc.sqlite3", ".sqlite3", "abc000", settings, wrapper)
        data.setup_storage()
        data.storage.connect()

        data.append('foo', 'bar')
        assert len(data.keys()) == 1

        assert data.value('foo') == 'bar'
        assert ["%s: %s" % (k, v) for k, v in data.storage][0] == "foo: bar"

        data.as_text() == "foo: bar"

def test_generic_data():
    with wrap() as wrapper:
        wrapper.to_walked()
        wrapper.to_checked()

        CONTENTS = "contents go here"

        # Create a GenericData object
        settings = {
                'canonical-name' : 'doc.txt'
                }
        data = dexy.data.Generic("doc.txt", ".txt", "abc000", settings, wrapper)
        data.setup_storage()

        # Assign some text contents
        data._data = CONTENTS
        assert data.has_data()
        assert not data.is_cached(True)

        # Save data to disk
        data.save()
        assert data.has_data()
        assert data.is_cached(True)
        assert data.filesize(True) > 10

        # Clear data from memory
        data._data = None

        # Load it again from disk
        data.load_data(True)
        assert data._data == CONTENTS

        assert data.as_text() == CONTENTS

def test_init_data():
    with wrap() as wrapper:
        settings = {
                'canonical-name' : 'doc.abc'
                }
        data = dexy.data.Generic("doc.txt", ".abc", "def123", settings, wrapper)
        data.setup_storage()

        assert data.key == "doc.txt"
        assert data.name == "doc.abc"
        assert data.ext == ".abc"
        assert data.storage_key == "def123"

        assert not data.has_data()
        assert not data.is_cached()
