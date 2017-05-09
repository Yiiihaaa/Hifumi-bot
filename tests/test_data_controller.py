from os.path import join
from unittest import TestCase, main

from core.data_controller import DataController


class TestDataController(TestCase):
    """
    Unittests for the DataController class
    """

    def setUp(self):
        """
        Setup before each test case
        """
        self.db = DataController(join('test_data', 'mock_db'))

    def tearDown(self):
        """
        Delete all data in mock_db after each test case
        :return:
        """
        conn = self.db.connection
        cur = self.db.cursor
        tables_sql = '''
        SELECT name FROM sqlite_master WHERE type=?
        '''
        cur.execute(tables_sql, ['table'])
        all_tables = [t[0] for t in cur.fetchall()]

        for name in all_tables:
            delete_sql = """
            DELETE FROM '{}'
            """.format(name)
            cur.execute(delete_sql)
        conn.commit()
        conn.close()

    def test_get_prefix_found(self):
        """
        Test case for get_prefix when it's found
        """
        self.db.set_prefix('foo', 'bar')
        prefix = self.db.get_prefix('foo')
        self.assertEqual(prefix, 'bar')

    def test_get_prefix_not_found(self):
        """
        Test for get_prefix when it's not found
        """
        self.db.set_prefix('bar', 'baz')
        self.assertIsNone(self.db.get_prefix('foo'))

    def test_set_prefix(self):
        """
        Test for set_preifx
        """
        server = 'foo'
        prefix = 'bar'
        self.db.set_prefix(server, prefix)
        self.assertEqual(prefix, self.db.get_prefix(server))

    def test_set_prefix_overwrite(self):
        """
        Test case for over write in set_preifx
        """
        server = 'foo'
        old_prefix = 'bar'
        new_prefix = 'baz'
        self.db.set_prefix(server, old_prefix)
        self.db.set_prefix(server, new_prefix)
        self.assertEqual(new_prefix, self.db.get_prefix(server))

    def test_write_tag(self):
        """
        Test case for write_tag
        """
        site = 'foo'
        tag = 'bar'
        self.db.write_tag(site, tag)
        sql = '''
        SELECT tag FROM main.nsfw_tags WHERE site='{}'
        '''.format(site)
        self.db.cursor.execute(sql)
        res = self.db.cursor.fetchone()[0]
        self.assertEqual(tag, res)

    def test_write_tag_list(self):
        """
        Test case for write_tag_list
        """
        site = 'foo'
        lst = ['bar', 'baz']
        self.db.write_tag_list(site, lst)
        sql = '''
        SELECT tag FROM main.nsfw_tags WHERE site='{}'
        '''.format(site)
        self.db.cursor.execute(sql)
        res = [t[0] for t in self.db.cursor.fetchall()]
        self.assertListEqual(lst, res)

    def test_tag_in_db_true(self):
        """
        Test for tag_in_db when it returns true
        """
        tag = 'foo'
        site = 'bar'
        self.db.write_tag(site, tag)
        self.assertTrue(self.db.tag_in_db(site, tag))

    def test_tag_in_db_no_site(self):
        """
        Test for tag_in_db when it returns False because site is not found
        """
        tag = 'foo'
        site = 'bar'
        wrong_site = 'baz'
        self.db.write_tag(site, tag)
        self.assertFalse(self.db.tag_in_db(wrong_site, tag))

    def test_tag_in_db_no_tag(self):
        """
        Test for tag_in_db when it returns False because tag is not found
        """
        tag = 'foo'
        site = 'bar'
        wrong_tag = 'baz'
        self.db.write_tag(site, tag)
        self.assertFalse(self.db.tag_in_db(site, wrong_tag))

    def test_fuzzy_match_tag_fail_site(self):
        """
        Test for fuzzy_match_tag when site is not found
        """
        site = 'foo'
        wrong_site = 'bar'
        tag = 'baz'
        self.db.write_tag(site, tag)
        self.assertIsNone(self.db.fuzzy_match_tag(wrong_site, tag))

    def test_fuzzy_match_tag_fail_tag(self):
        """
        Test for fuzzy_match_tag when tag is not found
        """
        site = 'foo'
        tag = 'bar'
        wrong_tag = 'baz'
        self.db.write_tag(site, tag)
        self.assertIsNone(self.db.fuzzy_match_tag(site, wrong_tag))

    def test_fuzzy_match_tag_front(self):
        """
        Test for fuzzy match tag when the front of the tag in db matched the
        search query
        """
        tag = 'foo'
        tag_to_match = 'f'
        site = 'bar'
        self.db.write_tag(site, tag)
        self.assertEqual(tag, self.db.fuzzy_match_tag(site, tag_to_match))

    def test_fuzzy_match_tag_middle(self):
        """
        Test for fuzzy match tag when the middle of the tag in db matched the
        search query
        """
        site = 'foo'
        tag = 'bar'
        tag_to_match = 'a'
        self.db.write_tag(site, tag)
        self.assertEqual(tag, self.db.fuzzy_match_tag(site, tag_to_match))

    def test_fuzzy_match_tag_end(self):
        """
        Test for fuzzy match tag when the back of the tag in db matched the
        search query
        """
        site = 'foo'
        tag = 'bar'
        tag_to_match = 'ar'
        self.db.write_tag(site, tag)
        self.assertEqual(tag, self.db.fuzzy_match_tag(site, tag_to_match))

    def test_fuzzy_match_tag_full(self):
        """
        Test for fuzzy match tag when the tag in db matched the
        search query
        """
        site = 'foo'
        tag = 'bar'
        tag_to_match = 'bar'
        self.db.write_tag(site, tag)
        self.assertEqual(tag, self.db.fuzzy_match_tag(site, tag_to_match))

    def test_get_language_success(self):
        """
        Test for get_language
        """
        server = 'foo'
        lan = 'bar'
        self.db.set_language(server, lan)
        self.assertEqual(lan, self.db.get_language(server))

    def test_get_language_fail(self):
        """
        Test for get_language when nothing is found
        """
        server = 'foo'
        self.assertIsNone(self.db.get_language(server))
        lan = 'bar'
        wrong_server = 'baz'
        self.db.set_language(server, lan)
        self.assertIsNone(self.db.get_language(wrong_server))

    def test_set_language(self):
        """
        Test for set_language
        """
        server = 'foo'
        lan = 'bar'
        self.db.set_language(server, lan)
        self.assertEqual(lan, self.db.get_language(server))

    def test_set_language_overwrite(self):
        """
        Test for set_language when it overrides the value
        """
        server = 'foo'
        old_lan = 'bar'
        new_lan = 'baz'
        self.db.set_language(server, old_lan)
        self.db.set_language(server, new_lan)
        self.assertEqual(new_lan, self.db.get_language(server))

    def test_add_role(self):
        """
        Test for add_role
        """
        server = 'foo'
        role = 'bar'
        self.db.add_role(server, role)
        self.assertTrue(role in self.db.get_role_list(server))

    def test_add_role_overwrite(self):
        """
        Test for add_role when it overrides the value
        """
        server = 'foo'
        role = 'bar'
        self.db.add_role(server, role)
        self.assertTrue(role in self.db.get_role_list(server))
        self.db.add_role(server, role)
        self.assertEqual(1, len(self.db.get_role_list(server)))

    def test_remove_role(self):
        """
        Test for remove role
        """
        server = 'foo'
        role = 'bar'
        other_roles = ['baz', 'qux']
        for r in [role] + other_roles:
            self.db.add_role(server, r)
        self.db.remove_role(server, role)
        self.assertListEqual(other_roles, self.db.get_role_list(server))

    def test_remove_role_no_server(self):
        """
        Test for remove role for a non-existing server
        """
        server = 'foo'
        wrong_server = 'bar'
        roles = ['baz', 'qux']
        for r in roles:
            self.db.add_role(server, r)
        self.db.remove_role(wrong_server, roles[0])
        self.assertListEqual(roles, self.db.get_role_list(server))

    def test_remove_role_no_role(self):
        """
        Test for remove role for a non-existing role
        :return:
        """
        server = 'foo'
        wrong_role = 'bar'
        roles = ['baz', 'qux']
        for r in roles:
            self.db.add_role(server, r)
        self.db.remove_role(server, wrong_role)
        self.assertListEqual(roles, self.db.get_role_list(server))

    def test_get_role_list(self):
        """
        Test for get_role_list
        """
        role_list = ['foo', 'bar']
        server = 'baz'
        for r in role_list:
            self.db.add_role(server, r)
        self.assertListEqual(role_list, self.db.get_role_list(server))

    def test_get_role_list_empty(self):
        """
        Test for get_role_list when it is empty
        """
        role_list = ['foo', 'bar']
        server = 'baz'
        wrong_server = 'qux'
        for r in role_list:
            self.db.add_role(server, r)
        self.assertListEqual([], self.db.get_role_list(wrong_server))


if __name__ == '__main__':
    main()