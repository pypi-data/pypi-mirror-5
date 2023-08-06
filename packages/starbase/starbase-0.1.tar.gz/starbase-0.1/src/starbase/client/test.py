import threading
import multiprocessing
import unittest
import uuid

import simple_timer

from starbase import Connection, Table

HOST = '127.0.0.1'
PORT = 8000
TABLE_NAME = 'messages'

COLUMN_FROM_USER = 'from_user'
FIELD_FROM_USER_ID = 'id'
FIELD_FROM_USER_NAME = 'name'
FIELD_FROM_USER_EMAIL = 'email'
FIELD_FROM_USER_AVATAR = 'avatar'

COLUMN_TO_USER = 'to_user'
FIELD_TO_USER_ID = 'id'
FIELD_TO_USER_NAME = 'name'
FIELD_TO_USER_EMAIL = 'email'
FIELD_TO_USER_AVATAR = 'avatar'

COLUMN_MESSAGE = 'message'
FIELD_MESSAGE_SUBJECT = 'subject'
FIELD_MESSAGE_BODY = 'body'
FIELD_MESSAGE_PRIVATE = 'private'
FIELD_MESSAGE_PRIORITY = 'priority'

TEST_ROW_KEY_1 = 'row1'
TEST_ROW_KEY_2 = 'row2'
TEST_ROW_KEY_3 = 'row3'

PRINT_INFO = True
TRACK_TIME = False
TEST_DELETE_TABLE = True
TEST_CREATE_TABLE = True

NUM_ROWS = 10
NUM_THREADS = 8
NUM_PROCESSES = 8

class Registry(object):
    pass

registry = Registry()

def print_info(func):
    """
    Prints some useful info.
    """
    if not PRINT_INFO:
        return func

    def inner(self, *args, **kwargs):
        if TRACK_TIME:
            timer = simple_timer.Timer() # Start timer

        result = func(self, *args, **kwargs)

        if TRACK_TIME:
            timer.stop() # Stop timer

        print '\n%s' % func.__name__
        print '============================'
        if func.__doc__:
            print '""" %s """' % func.__doc__.strip()
        print '----------------------------'
        if result is not None: print result
        if TRACK_TIME:
            print 'done in %s seconds' % timer.duration

        return result
    return inner

class StarbaseClient01ConnectionTest(unittest.TestCase):
    """
    Starbase Connection tests.
    """
    #@print_info
    def setUp(self):
        self.connection = Connection(HOST, PORT, content_type='json')
        self.table = self.connection.table(TABLE_NAME)

    @print_info
    def test_01_version(self):
        res = self.connection.version
        self.assertIsInstance(res, dict)
        return res

    @print_info
    def test_02_cluster_version(self):
        res = self.connection.cluster_version
        self.assertIsInstance(res, unicode)
        return res

    @print_info
    def test_03_cluster_status(self):
        res = self.connection.cluster_status
        self.assertIsInstance(res, dict)
        return res

    if TEST_DELETE_TABLE:
        @print_info
        def test_04_drop_table_schema(self):
            """
            Delete table schema. Deleting the table if it exists. After that checking if table still exists.
            """
            # First testing for non-existent table
            non_existent_res = self.connection.table('non-existent-table').drop()
            self.assertEqual(503, non_existent_res)

            res = None
            if self.connection.table_exists(TABLE_NAME):
                res = self.connection.table(TABLE_NAME).drop()
                self.assertEqual(200, res) # Checking the status code
                self.assertTrue(not self.connection.table_exists(TABLE_NAME)) # Checking for physical existence

            return non_existent_res, res

    if TEST_CREATE_TABLE:
        @print_info
        def test_05_create_table_schema(self):
            """
            Create table schema. After creating the table we just check if it exists.
            """
            # Success tests
            res = None
            if not self.connection.table_exists(TABLE_NAME):
                columns = [COLUMN_FROM_USER, COLUMN_TO_USER, COLUMN_MESSAGE]

                res = self.connection.table(TABLE_NAME).create(*columns)

            self.assertTrue(self.connection.table_exists(TABLE_NAME))

            # Now trying to create a table even if it exists.
            columns = [COLUMN_FROM_USER, COLUMN_TO_USER, COLUMN_MESSAGE]
            res_fail = self.connection.table(TABLE_NAME).create(*columns)
            self.assertEqual(res_fail, False)

            return res, res_fail

    @print_info
    def test_06_get_table_schema(self):
        """
        Get table schema.
        """
        # First testing for non existent table
        non_existent_table = self.connection.table('non-existent-table')
        self.assertTrue(non_existent_table.schema() is None)

        # Now for existing one
        res = self.table.schema()
        self.assertTrue(res is not None)
        return non_existent_table, res

    @print_info
    def test_07_table_list(self):
        res = self.connection.tables()
        self.assertIsInstance(res, list)

        self.assertIn(TABLE_NAME, res)
        return res


class StarbaseClient02TableTest(unittest.TestCase):
    """
    Starbase Table tests.
    """
    def setUp(self):
        self.connection = Connection(HOST, PORT, content_type='json')
        self.table = self.connection.table(TABLE_NAME)

    @print_info
    def test_01_columns_list(self):
        res = self.table.columns()
        self.assertIsInstance(res, list)

        self.assertIn(COLUMN_FROM_USER, res)
        self.assertIn(COLUMN_TO_USER, res)
        self.assertIn(COLUMN_MESSAGE, res)
        return res

    @print_info
    def test_04a_table_put_multiple_column_data(self, process_number=0, perfect_dict=False):
        """
        Insert multiple-colums into a single row of HBase using Stagate REST API using normal dict as input.
        """
        # Success test
        key = 'row_%s_%s' % (('perfect_' if perfect_dict else ''), str(uuid.uuid4()))

        columns = {}

        if perfect_dict:
            columns = {
                COLUMN_FROM_USER: {
                    FIELD_FROM_USER_ID: '123',
                    FIELD_FROM_USER_NAME: 'John Doe',
                    FIELD_FROM_USER_EMAIL: 'john@doe.com'
                },
                COLUMN_TO_USER: {
                    FIELD_TO_USER_ID: '456',
                    FIELD_TO_USER_NAME: 'Lorem Ipsum',
                    FIELD_TO_USER_EMAIL: 'lorem@ipsum.com'
                },
                COLUMN_MESSAGE: {
                    FIELD_MESSAGE_SUBJECT: 'Lorem ipsum',
                    FIELD_MESSAGE_BODY: 'Lorem ipsum dolor sit amet.'
                },
            }
        else:
            columns = {
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): '123',
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME): 'John Doe',
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL): 'john@doe.com',
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID): '456',
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME): 'Lorem Ipsum',
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL): 'lorem@ipsum.com',
                '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT): 'Lorem ipsum',
                '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY): 'Lorem ipsum dolor sit amet.'
            }

        res = self.table.insert(key, columns)
        self.assertEqual(res, 200)
        return res

    def test_04b_table_put_multiple_column_data_normal_dict(self, process_number=0):
        """
        Insert multiple-colums into a single row of HBase using Stagate REST API using perfect dict as input.
        """
        return self.test_04a_table_put_multiple_column_data(process_number=process_number, perfect_dict=True)

    @print_info
    def test_05a_table_batch_put_multiple_column_data(self, process_number=0, perfect_dict=False):
        """
        Insert multiple-colums in batch into a HBase using Stagate REST API using normal dict as input.
        """
        batch = self.table.batch()

        keys = []
        for i in range(0, NUM_ROWS):
            key = 'row_%s_%s' % (('perfect_' if perfect_dict else ''), str(uuid.uuid4()))
            keys.append(key)

            columns = {}

            if perfect_dict:
                columns = {
                    COLUMN_FROM_USER: {
                        FIELD_FROM_USER_ID: '123',
                        FIELD_FROM_USER_NAME: 'John Doe',
                        FIELD_FROM_USER_EMAIL: 'john@doe.com'
                    },
                    COLUMN_TO_USER: {
                        FIELD_TO_USER_ID: '456',
                        FIELD_TO_USER_NAME: 'Lorem Ipsum',
                        FIELD_TO_USER_EMAIL: 'lorem@ipsum.com'
                    },
                    COLUMN_MESSAGE: {
                        FIELD_MESSAGE_SUBJECT: 'Lorem ipsum',
                        FIELD_MESSAGE_BODY: 'Lorem ipsum dolor sit amet.'
                    },
                }
            else:
                columns = {
                    '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): '123',
                    '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME): 'John Doe',
                    '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL): 'john@doe.com',
                    '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID): '456',
                    '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME): 'Lorem Ipsum',
                    '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL): 'lorem@ipsum.com',
                    '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT): 'Lorem ipsum',
                    '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY): 'Lorem ipsum dolor sit amet.'
                }

            batch.insert(key, columns)

        res = batch.commit(finalize=True)
        self.assertEqual(res.get('response', None), [200])
        registry.keys = keys
        return res

    def test_05b_table_batch_put_multiple_column_data_perfect_dict(self, process_number=0):
        """
        Insert multiple-colums in batch into a HBase using Stagate REST API using perfect dict as input.
        """
        return self.test_05a_table_batch_put_multiple_column_data(process_number=process_number, perfect_dict=True)

    @print_info
    def test_05c_table_batch_post_multiple_column_data(self, process_number=0, perfect_dict=False):
        """
        Update multiple-colums in batch into a HBase using Stagate REST API using normal dict as input.
        """
        # Updating the records inserted by `test_05a_table_batch_put_multiple_column_data` and
        # `test_05b_table_batch_put_multiple_column_data_perfect_dict`.
        batch = self.table.batch()

        for key in registry.keys:
            columns = {}

            if perfect_dict:
                columns = {
                    COLUMN_FROM_USER: {
                        FIELD_FROM_USER_AVATAR: '://example.com/avatar_from_user.jpg',
                    },
                    COLUMN_TO_USER: {
                        FIELD_TO_USER_AVATAR: '://example.com/avatar_to_user.jpg',
                    },
                    COLUMN_MESSAGE: {
                        FIELD_MESSAGE_PRIVATE: '1',
                        FIELD_MESSAGE_PRIORITY: 'high'
                    },
                }
            else:
                columns = {
                    '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_AVATAR): '://example.com/avatar_from_user.jpg',
                    '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_AVATAR): '://example.com/avatar_to_user.jpg',
                    '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_PRIVATE): '1',
                    '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_PRIORITY): 'high'
                }

            batch.update(key, columns)

        res = batch.commit(finalize=True)
        self.assertEqual(res.get('response', None), [200])


        if perfect_dict:
            output = {
                COLUMN_FROM_USER: {
                    FIELD_FROM_USER_ID: '123',
                    FIELD_FROM_USER_NAME: 'John Doe',
                    FIELD_FROM_USER_EMAIL: 'john@doe.com',
                    FIELD_FROM_USER_AVATAR: '://example.com/avatar_from_user.jpg',
                },
                COLUMN_TO_USER: {
                    FIELD_TO_USER_ID: '456',
                    FIELD_TO_USER_NAME: 'Lorem Ipsum',
                    FIELD_TO_USER_EMAIL: 'lorem@ipsum.com',
                    FIELD_TO_USER_AVATAR: '://example.com/avatar_to_user.jpg',
                },
                COLUMN_MESSAGE: {
                    FIELD_MESSAGE_SUBJECT: 'Lorem ipsum',
                    FIELD_MESSAGE_BODY: 'Lorem ipsum dolor sit amet.',
                    FIELD_MESSAGE_PRIVATE: '1',
                    FIELD_MESSAGE_PRIORITY: 'high'
                }
            }
        else:
            output = {
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): '123',
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME): 'John Doe',
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL): 'john@doe.com',
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_AVATAR): '://example.com/avatar_from_user.jpg',
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID): '456',
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME): 'Lorem Ipsum',
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL): 'lorem@ipsum.com',
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_AVATAR): '://example.com/avatar_to_user.jpg',
                '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT): 'Lorem ipsum',
                '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY): 'Lorem ipsum dolor sit amet.',
                '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_PRIVATE): '1',
                '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_PRIORITY): 'high'
            }

        # Now testing the data
        rows = []
        for key in registry.keys:
            row = self.table.fetch(key, perfect_dict=perfect_dict)
            self.assertEqual(row, output)
            rows.append(row)

        return res

    def test_05d_table_batch_post_multiple_column_data_perfect_dict(self, process_number=0):
        """
        Update multiple-colums in batch into a HBase using Stagate REST API using perfect dict as input.
        """
        return self.test_05c_table_batch_post_multiple_column_data(process_number=process_number, perfect_dict=True)

    @print_info
    def test_06_table_put_column_data(self, process_number=0):
        """
        Insert single column data into a single row of HBase using starbase REST API.
        """
        key = 'row_1_'
        res = []
        num_rows = NUM_ROWS

        for i in xrange(num_rows):
            columns = {
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): str(11 * (i + 1)),
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME): 'John Doe',
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL): 'john@doe.net',
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID): str(22 * (i + 1)),
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME): 'Lorem Ipsum',
                '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL): 'lorem@ipsum.net',
                '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT): 'Lorem ipsum',
                '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY): 'Lorem ipsum dolor sit amet.',
                }
            res.append(self.table.insert('%s%s' % (key, i), columns))

        self.assertEqual(res, [200 for i in xrange(num_rows)])
        return res

    @print_info
    def test_07a_table_put_column_data(self, process_number=0):
        """
        Insert single column data into a single row of HBase using starbase REST API.

        ..note: Used in ``test_09_table_post_column_data``.
        """
        key = 'row_1_abcdef'

        columns = {
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): '110',
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME): 'John Doe',
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL): 'john@doe.net',
            #'%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID): '220',
            #'%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME): 'Lorem Ipsum',
            #'%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL): 'lorem@ipsum.net',
            #'%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT): 'Lorem ipsum',
            #'%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY): 'Lorem ipsum dolor sit amet.',
            }
        res = self.table.insert(key, columns)
        self.assertEqual(res, 200)
        return res

    @print_info
    def test_07b_table_put_column_data(self, process_number=0):
        """
        Insert multiple column data into a single row of HBase using starbase REST API.

        ..note: Used in ``test_08a_get_single_row_with_all_columns`` and ``test_08b_get_single_row_with_all_columns``.
        """
        key = 'row_2_abcdef'

        columns = {
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): '110',
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME): 'John Doe',
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL): 'john@doe.net',
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID): '220',
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME): 'Lorem Ipsum',
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL): 'lorem@ipsum.net',
            '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT): 'Lorem ipsum',
            '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY): 'Lorem ipsum dolor sit amet.',
            }
        res = self.table.insert(key, columns)
        self.assertEqual(res, 200)
        return res

    @print_info
    def test_08a_get_single_row_with_all_columns(self, row_key='row_2_abcdef'):
        """
        Fetches a single row from HBase using starbase REST API with all columns of that row as simple dict.
        """
        res = self.table.fetch(row=row_key, perfect_dict=False)
        output = {
            'from_user:id': '110',
            'from_user:name': 'John Doe',
            'from_user:email': 'john@doe.net',
            'message:body': 'Lorem ipsum dolor sit amet.',
            'message:subject': 'Lorem ipsum',
            'to_user:id': '220',
            'to_user:name': 'Lorem Ipsum',
            'to_user:email': 'lorem@ipsum.net'
        }
        self.assertEqual(res, output)
        return res

    @print_info
    def test_08b_get_single_row_with_all_columns_as_perfect_dict(self, row_key='row_2_abcdef'):
        """
        Fetches a single row from HBase using starbase REST API with all columns of that row as perfect dict.
        """
        res = self.table.fetch(row=row_key, perfect_dict=True)
        output = {
            'to_user': {'id': '220', 'name': 'Lorem Ipsum', 'email': 'lorem@ipsum.net'},
            'message': {'body': 'Lorem ipsum dolor sit amet.', 'subject': 'Lorem ipsum'},
            'from_user': {'id': '110', 'name': 'John Doe', 'email': 'john@doe.net'}
        }
        self.assertEqual(res, output)
        return res

    @print_info
    def test_09_table_post_column_data(self, process_number=0):
        """
        Updates (POST) data of a single row of HBase using starbase REST API. Updates data set in
        ``test_07a_table_put_column_data``.
        """
        key = 'row_1_abcdef'

        columns = {
            #'%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): '110',
            #'%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME): 'John Doe',
            #'%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL): 'john@doe.net',
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID): '220',
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME): 'Lorem Ipsum',
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL): 'lorem@ipsum.net',
            '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT): 'Lorem ipsum',
            '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY): 'Lorem ipsum dolor sit amet.',
            }

        output = {
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): '110',
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME): 'John Doe',
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL): 'john@doe.net',
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID): '220',
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME): 'Lorem Ipsum',
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL): 'lorem@ipsum.net',
            '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT): 'Lorem ipsum',
            '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY): 'Lorem ipsum dolor sit amet.',
            }
        res = self.table.insert(key, columns)

        #print 'expected output: ', output

        check_response = self.table.fetch(row=key, perfect_dict=False)

        #print 'response received: ', check_response
        return res

    @print_info
    def test_10_get_single_row_with_all_columns(self, row_key='row_1_abcdef'):
        """
        Fetches a single row from HBase using starbase REST API with all columns of that row.
        """
        res = self.table.fetch(row=row_key, perfect_dict=True)
        output = {
            'to_user': {'id': '220', 'email': 'lorem@ipsum.net', 'name': 'Lorem Ipsum'},
            'message': {'body': 'Lorem ipsum dolor sit amet.',
            'subject': 'Lorem ipsum'},
            'from_user': {'id': '110', 'name': 'John Doe', 'email': 'john@doe.net'}
        }
        self.assertEqual(res, output)
        return res

    @print_info
    def test_11_table_delete_rows_one_by_one(self, process_number=0):
        """
        Insert single column data into a single row of HBase using starbase REST API. Deletes data set by
        ``test_06_table_put_column_data`` (all except the last record)..
        """
        key = 'row_1_'
        res = []
        num_rows = NUM_ROWS - 1
        output = []
        for i in xrange(num_rows):
            columns = {
                '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): str(11 * (i + 1)),
                }
            res.append(self.table.remove('%s%s' % (key, i)))
            output.append(200)

        self.assertEqual(res, output)

        return res

    @print_info
    def test_12_get_single_row_with_all_columns(self, row_key='row_1_9'):
        """
        Fetches a single row from HBase using starbase REST API with all columns of that row.
        """
        res = self.table.fetch(row=row_key, perfect_dict=True)
        output = {
            'to_user': {'id': '220', 'email': 'lorem@ipsum.net', 'name': 'Lorem Ipsum'},
            'message': {'body': 'Lorem ipsum dolor sit amet.', 'subject': 'Lorem ipsum'},
            'from_user': {'id': '110', 'email': 'john@doe.net', 'name': 'John Doe'}
        }
        self.assertEqual(res, output)

        return res

    @print_info
    def test_13a_get_single_row_with_selective_columns(self, row_key='row_1_9'):
        """
        Fetches a single row selective columns from HBase using starbase REST API.
        """
        # Columns to fetch (normal list)
        columns = [
            '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID),
            #'%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME),
            #'%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL),
            
            '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID),
            #'%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME),
            #'%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL),

            #'%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT),
            #'%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY),
        ]

        # Get table row data
        res = self.table.fetch(row=TEST_ROW_KEY_1, columns=columns, perfect_dict=True)

        return res

    @print_info
    def test_13b_get_single_row_with_selective_columns(self, row_key='row_1_9'):
        """
        Fetches a single row selective columns from HBase using starbase REST API.
        """
        t = self.connection.table('register')
        t.create('users', 'groups', 'sites', 'messages')

        data = {
            'users': {'id': '1', 'name': 'Artur Barseghyan', 'email': 'artur.barseghyan@gmail.com'},
            'groups': {'id': '1', 'name': 'admins'},
            'sites': {'url': ['http://foreverchild.info', 'http://delusionalinsanity.com']},
        }

        # Note, that since we're inserting a structure into HBase cell, it's automatically turned into a string.
        # In this case the data inserted won't be equal to the data fetched.
        output_data = {
            'users': {'email': 'artur.barseghyan@gmail.com', 'name': 'Artur Barseghyan', 'id': '1'},
            'groups': {'id': '1', 'name': 'admins'},
            'sites': {'url': "['http://foreverchild.info', 'http://delusionalinsanity.com']"}
        }

        res = t.insert('aaa', data)

        self.assertEqual(res, 200)

        # Getting entire row
        res = t.fetch('aaa')
        self.assertEqual(res, output_data)

        # Getting selected columns
        res = t.fetch('aaa', ['users', 'groups'])
        self.assertEqual(res, {'users': data['users'], 'groups': data['groups']})

        # Getting selected cells only
        res = t.fetch('aaa', {'users': ['id', 'email'], 'sites': ['url']})
        output_data['users'].pop('name')
        output_data.pop('groups')
        self.assertEqual(res, output_data)

        return res

    @print_info
    def test_14_table_get_all_rows(self, raw=True, perfect_dict=True):
        """
        Get all rows.
        """
        res = list(self.table.fetch_all_rows(perfect_dict=perfect_dict))
        self.assertEqual(res[0]['to_user'], {'id': '220', 'email': 'lorem@ipsum.net', 'name': 'Lorem Ipsum'})
        self.assertEqual(res[1]['from_user'], {'id': '110', 'name': 'John Doe', 'email': 'john@doe.net'})
        return res

    #@print_info
    def test_15_table_put_multiple_column_data_in_multithreading(self, number_of_threads=NUM_THREADS):
        """
        Speed test.
        """
        def local_test():
            key = 'row_1_'
            results = []
            num_rows = NUM_ROWS

            for i in xrange(num_rows):
                columns = {
                    '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID): str(11 * (i + 1)),
                    '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_NAME): 'John Doe',
                    '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL): 'john@doe.net',
                    '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID): str(22 * (i + 1)),
                    '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_NAME): 'Lorem Ipsum',
                    '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL): 'lorem@ipsum.net',
                    '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT): 'Lorem ipsum',
                    '%s:%s' % (COLUMN_MESSAGE, FIELD_MESSAGE_BODY): 'Lorem ipsum dolor sit amet.',
                    }
                results.append(self.table.insert('%s%s' % (key, i), columns))
            return results

        timer = simple_timer.Timer()

        threads = []

        for thread_number in xrange(number_of_threads):
            t = threading.Thread(target=local_test, args=[])
            threads.append(t)
            t.start()

        [t.join() for t in threads]

        print 'test_15_table_put_multiple_column_data_in_multithreading'
        print "=============================="
        print '%s records inserted in total' % (number_of_threads * NUM_ROWS)
        print "total number of threads %s" % number_of_threads
        print "%s seconds elapsed" % timer.stop_and_return_duration()
        print "making it %s of records inserted per second\n" % \
              (number_of_threads * NUM_ROWS / timer.duration)

    @print_info
    def test_16_table_delete_row(self):
        """
        Delete row.
        """
        # First create a row.
        row = 'aaa'
        data = {
            COLUMN_MESSAGE: {FIELD_MESSAGE_SUBJECT: 'subject aaa', FIELD_MESSAGE_BODY: 'body aaa'},
            COLUMN_FROM_USER: {FIELD_FROM_USER_ID: '1', FIELD_FROM_USER_NAME: 'fr@m.com'}
        }
        res = self.table.insert(row, data)
        self.assertEqual(res, 200)

        # Get the row and make sure the result is equal
        res = self.table.fetch(row)
        self.assertEqual(res, data)

        # Now first delete the single cell from the row.
        res = self.table.remove(row, COLUMN_MESSAGE, FIELD_MESSAGE_SUBJECT)
        self.assertEqual(res, 200)

        # Make sure it's definitely gone
        res = self.table.fetch(row)
        data[COLUMN_MESSAGE].pop(FIELD_MESSAGE_SUBJECT) # Remove the element
        self.assertEqual(res, data)

        # Now deleting entire column
        res = self.table.remove(row, COLUMN_FROM_USER)
        self.assertEqual(res, 200)

        # Make sure it's definitely gone
        res = self.table.fetch(row)
        data.pop(COLUMN_FROM_USER) # Remove the element
        self.assertEqual(res, data)

        # Delete entire row
        res = self.table.remove(row)
        self.assertEqual(res, 200)

        # Make sure it's definitely gone
        res = self.table.fetch(row)
        self.assertTrue(not res)

        return res

    @print_info
    def test_17_alter_table(self):
        """
        Testing altering the table (add/remove columns).
        """
        # First creating a new table
        t = self.connection.table('new_table')

        if t.exists():
            t.drop()

        res = t.create('first_col', 'second_col', 'third_col')
        self.assertEqual(res, 201)

        # Make sure it's barely there
        res = t.columns()
        res.sort()
        cols = ['first_col', 'second_col', 'third_col']
        cols.sort()
        self.assertEqual(res, cols)

        # Now add more columns
        res = t.add_columns('fourth', 'fifth')
        self.assertEqual(res, 200)

        # Make sure it's barely there
        res = t.columns()
        res.sort()
        cols = ['first_col', 'second_col', 'third_col', 'fourth', 'fifth']
        cols.sort()
        self.assertEqual(res, cols)

        return res

    def __set_test_16_data(self):
        """
        Not a test. Just sets some data for test #16.
        """
        # ***************** Input data *******************
        self.sample_1 = {
               "Row": {
                  "key": "key1",
                  "Cell": {
                     "column": "ColFam:Col1",
                     "$": "someData"
                  }
               }
            }

        self.sample_2 = {
               "Row":
                  {
                     "key": "key1",
                     "Cell": [
                        {
                           "column": "ColFam:Col1",
                           "$": "someData"
                        },
                        {
                           "column": "ColFam:Col2",
                           "$": "moreData"
                        }
                     ]
                  }
            }

        self.sample_3 = {
               "Row":[
                  {
                     "key": "key1",
                     "Cell": [
                        {
                           "column": "ColFam:Col1",
                           "$": "someData"
                        },
                        {
                           "column": "ColFam:Col2",
                           "$": "moreData"
                        },
                     ]
                  },
                  {
                     "key": "key2",
                     "Cell": [
                        {
                           "column": "ColFam:Col1",
                           "$": "someData2"
                        },
                        {
                           "column": "ColFam:Col2",
                           "$": "moreData2"
                        },
                     ]
                  }

               ]
            }

        self.sample_4 = {
            u'Row': {
                u'Cell': [
                    {u'column': '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_ID), \
                     u'timestamp': '1369247627546', u'$': '123'},
                    {u'column': '%s:%s' % (COLUMN_FROM_USER, FIELD_FROM_USER_EMAIL), \
                     u'timestamp': '1369247627546', u'$': 'john@doe.com'},
                    {u'column': '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_ID), \
                     u'timestamp': '1369247627546', u'$': '345'},
                    {u'column': '%s:%s' % (COLUMN_TO_USER, FIELD_TO_USER_EMAIL), \
                     u'timestamp': '1369247627546', u'$': 'lorem@ipsum.com'},
                ],
                u'key': 'row81d70d7c-8f30-42fd-be1c-772308b25889908'
            }
        }

        # ***************** Expected output data *******************
        self.sample_1_output_pd = {'ColFam': {'Col1': 'someData'}}

        self.sample_2_output_pd = {'ColFam': {'Col2': 'moreData', 'Col1': 'someData'}} 

        self.sample_3_output_pd = [
            {'ColFam': {'Col2': 'moreData', 'Col1': 'someData'}},
            {'ColFam': {'Col2': 'moreData2', 'Col1': 'someData2'}}
        ]

        self.sample_4_output_pd = {
            'to_user': {'id': '345', 'email': 'lorem@ipsum.com'},
            'from_user': {'id': '123', 'email': 'john@doe.com'}
        }

        self.sample_1_output = {'ColFam:Col1': 'someData'}

        self.sample_2_output = {'ColFam:Col1': 'someData', 'ColFam:Col2': 'moreData'}

        self.sample_3_output = [
            {'ColFam:Col1': 'someData', 'ColFam:Col2': 'moreData'},
            {'ColFam:Col1': 'someData2', 'ColFam:Col2': 'moreData2'}
        ]

        self.sample_4_output = {
            'to_user:id': '345',
            'from_user:id': '123',
            'to_user:email': 'lorem@ipsum.com',
            'from_user:email': 'john@doe.com'
        }

    @print_info
    def test_18a_test_extract_usable_data_as_perfect_dict(self):
        """
        Test ``_extract_usable_data`` method of ``starbase.client.Table`` as perfect dict.
        """
        self.__set_test_16_data()

        r1 = Table._extract_usable_data(self.sample_1, perfect_dict=True)
        self.assertEqual(r1, self.sample_1_output_pd)

        r2 = Table._extract_usable_data(self.sample_2, perfect_dict=True)
        self.assertEqual(r2,self.sample_2_output_pd)

        r3 = Table._extract_usable_data(self.sample_3, perfect_dict=True)
        self.assertEqual(r3,self.sample_3_output_pd)

        r4 = Table._extract_usable_data(self.sample_4, perfect_dict=True)
        self.assertEqual(r4, self.sample_4_output_pd)

        return (r1, r2, r3, r4)

    @print_info
    def test_18b_test_extract_usable_data(self):
        """
        Test ``_extract_usable_data`` method of ``starbase.client.Table`` as normal dict.
        """
        self.__set_test_16_data()

        r1 = Table._extract_usable_data(self.sample_1, perfect_dict=False)
        self.assertEqual(r1, self.sample_1_output)

        r2 = Table._extract_usable_data(self.sample_2, perfect_dict=False)
        self.assertEqual(r2, self.sample_2_output)

        r3 = Table._extract_usable_data(self.sample_3, perfect_dict=False)
        self.assertEqual(r3, self.sample_3_output)

        r4 = Table._extract_usable_data(self.sample_4, perfect_dict=False)
        self.assertEqual(r4,self.sample_4_output)

        return (r1, r2, r3, r4)


if __name__ == '__main__':
    unittest.main()
