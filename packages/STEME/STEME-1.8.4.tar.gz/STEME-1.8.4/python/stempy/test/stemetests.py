import os
import stemewebapp
import unittest
import tempfile

class StemeTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, stemewebapp.app.config['DATABASE'] = tempfile.mkstemp()
        stemewebapp.app.config['TESTING'] = True
        self.app = stemewebapp.app.test_client()
        stemewebapp.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(stemewebapp.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No entries here so far' in rv.data
    
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)
    
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    
    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert 'Invalid username' in rv.data
        rv = self.login('admin', 'defaultx')
        assert 'Invalid password' in rv.data

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data
           
if __name__ == '__main__':
    unittest.main()
    