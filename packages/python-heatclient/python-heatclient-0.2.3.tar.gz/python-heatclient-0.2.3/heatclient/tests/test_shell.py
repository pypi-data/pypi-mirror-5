import cStringIO
import httplib2
import os
import re
import sys
import urllib2
import yaml

import fixtures
import mox
import testscenarios
import testtools

try:
    import json
except ImportError:
    import simplejson as json
from keystoneclient.v2_0 import client as ksclient

from heatclient import exc
import heatclient.shell
from heatclient.tests import fakes
from heatclient.v1 import client as v1client
from heatclient.v1 import shell as v1shell


load_tests = testscenarios.load_tests_apply_scenarios
TEST_VAR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            'var'))


class TestCase(testtools.TestCase):

    def set_fake_env(self, fake_env):
        for key, value in fake_env.items():
            self.useFixture(fixtures.EnvironmentVariable(key, value))

    # required for testing with Python 2.6
    def assertRegexpMatches(self, text, expected_regexp, msg=None):
        """Fail the test unless the text matches the regular expression."""
        if isinstance(expected_regexp, basestring):
            expected_regexp = re.compile(expected_regexp)
        if not expected_regexp.search(text):
            msg = msg or "Regexp didn't match"
            msg = '%s: %r not found in %r' % (
                msg, expected_regexp.pattern, text)
            raise self.failureException(msg)

    def shell_error(self, argstr, error_match):
        orig = sys.stderr
        try:
            sys.stderr = cStringIO.StringIO()
            _shell = heatclient.shell.HeatShell()
            _shell.main(argstr.split())
        except exc.CommandError as e:
            self.assertRegexpMatches(e.__str__(), error_match)
        else:
            self.fail('Expected error matching: %s' % error_match)
        finally:
            err = sys.stderr.getvalue()
            sys.stderr.close()
            sys.stderr = orig
        return err


class EnvVarTest(TestCase):

    scenarios = [
        ('username', dict(
            remove='OS_USERNAME',
            err='You must provide a username')),
        ('password', dict(
            remove='OS_PASSWORD',
            err='You must provide a password')),
        ('tenant_name', dict(
            remove='OS_TENANT_NAME',
            err='You must provide a tenant_id')),
        ('auth_url', dict(
            remove='OS_AUTH_URL',
            err='You must provide an auth url')),
    ]

    def test_missing_auth(self):

        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        fake_env[self.remove] = None
        self.set_fake_env(fake_env)
        self.shell_error('list', self.err)


class ShellParamValidationTest(TestCase):

    scenarios = [
        ('create', dict(
            command='create ts -P "a!b"',
            err='Malformed parameter')),
        ('stack-create', dict(
            command='stack-create ts -P "ab"',
            err='Malformed parameter')),
        ('update', dict(
            command='update ts -P "a~b"',
            err='Malformed parameter')),
        ('stack-update', dict(
            command='stack-update ts -P "a-b"',
            err='Malformed parameter')),
        ('validate', dict(
            command='validate -P "a=b;c"',
            err='Malformed parameter')),
        ('template-validate', dict(
            command='template-validate -P "a$b"',
            err='Malformed parameter')),
    ]

    def setUp(self):
        super(ShellParamValidationTest, self).setUp()
        self.m = mox.Mox()
        self.addCleanup(self.m.VerifyAll)
        self.addCleanup(self.m.UnsetStubs)

    def test_bad_parameters(self):
        self.m.StubOutWithMock(ksclient, 'Client')
        self.m.StubOutWithMock(v1client.Client, 'json_request')
        fakes.script_keystone_client()

        self.m.ReplayAll()
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)
        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        cmd = '%s --template-file=%s ' % (self.command, template_file)
        self.shell_error(cmd, self.err)


class ShellValidationTest(TestCase):

    def setUp(self):
        super(ShellValidationTest, self).setUp()
        self.m = mox.Mox()
        self.addCleanup(self.m.VerifyAll)
        self.addCleanup(self.m.UnsetStubs)

    def test_failed_auth(self):
        self.m.StubOutWithMock(ksclient, 'Client')
        self.m.StubOutWithMock(v1client.Client, 'json_request')
        fakes.script_keystone_client()
        v1client.Client.json_request(
            'GET', '/stacks?limit=20').AndRaise(exc.Unauthorized)

        self.m.ReplayAll()
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)
        self.shell_error('list', 'Invalid OpenStack Identity credentials.')

    def test_create_validation(self):
        self.m.StubOutWithMock(ksclient, 'Client')
        self.m.StubOutWithMock(v1client.Client, 'json_request')
        fakes.script_keystone_client()

        self.m.ReplayAll()
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)
        self.shell_error(
            'create teststack '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"',
            'Need to specify exactly one of')


class ShellTest(TestCase):

    # Patch os.environ to avoid required auth info.
    def setUp(self):
        super(ShellTest, self).setUp()
        self.m = mox.Mox()
        self.m.StubOutWithMock(ksclient, 'Client')
        self.m.StubOutWithMock(v1client.Client, 'json_request')
        self.m.StubOutWithMock(v1client.Client, 'raw_request')
        self.addCleanup(self.m.VerifyAll)
        self.addCleanup(self.m.UnsetStubs)
        fake_env = {
            'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
        }
        self.set_fake_env(fake_env)

    def shell(self, argstr):
        orig = sys.stdout
        try:
            sys.stdout = cStringIO.StringIO()
            _shell = heatclient.shell.HeatShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(exc_value.code, 0)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig

        return out

    def test_help_unknown_command(self):
        self.assertRaises(exc.CommandError, self.shell, 'help foofoo')

    def test_debug(self):
        httplib2.debuglevel = 0
        self.shell('--debug help')
        self.assertEqual(httplib2.debuglevel, 1)

    def test_help(self):
        required = [
            '^usage: heat',
            '(?m)^See "heat help COMMAND" for help on a specific command',
        ]
        for argstr in ['--help', 'help']:
            help_text = self.shell(argstr)
            for r in required:
                self.assertRegexpMatches(help_text, r)

    def test_help_on_subcommand(self):
        required = [
            '^usage: heat stack-list',
            "(?m)^List the user's stacks",
        ]
        argstrings = [
            'help stack-list',
        ]
        for argstr in argstrings:
            help_text = self.shell(argstr)
            for r in required:
                self.assertRegexpMatches(help_text, r)

    def test_list(self):
        fakes.script_keystone_client()
        fakes.script_heat_list()

        self.m.ReplayAll()

        list_text = self.shell('list')

        required = [
            'id',
            'stack_status',
            'creation_time',
            'teststack',
            '1',
            'CREATE_COMPLETE',
            'IN_PROGRESS',
        ]
        for r in required:
            self.assertRegexpMatches(list_text, r)

    def test_describe(self):
        fakes.script_keystone_client()
        resp_dict = {"stack": {
            "id": "1",
            "stack_name": "teststack",
            "stack_status": 'CREATE_COMPLETE',
            "creation_time": "2012-10-25T01:58:47Z"
        }}
        resp = fakes.FakeHTTPResponse(
            200,
            'OK',
            {'content-type': 'application/json'},
            json.dumps(resp_dict))
        v1client.Client.json_request(
            'GET', '/stacks/teststack/1').AndReturn((resp, resp_dict))

        self.m.ReplayAll()

        list_text = self.shell('describe teststack/1')

        required = [
            'id',
            'stack_name',
            'stack_status',
            'creation_time',
            'teststack',
            'CREATE_COMPLETE',
            '2012-10-25T01:58:47Z'
        ]
        for r in required:
            self.assertRegexpMatches(list_text, r)

    def test_create(self):
        fakes.script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            201,
            'Created',
            {'location': 'http://no.where/v1/tenant_id/stacks/teststack2/2'},
            None)
        v1client.Client.json_request(
            'POST', '/stacks', body=mox.IgnoreArg(),
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        create_text = self.shell(
            'create teststack '
            '--template-file=%s '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"' % template_file)

        required = [
            'stack_name',
            'id',
            'teststack',
            '1'
        ]

        for r in required:
            self.assertRegexpMatches(create_text, r)

    def test_create_url(self):

        fakes.script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            201,
            'Created',
            {'location': 'http://no.where/v1/tenant_id/stacks/teststack2/2'},
            None)
        v1client.Client.json_request(
            'POST', '/stacks', body=mox.IgnoreArg(),
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        create_text = self.shell(
            'create teststack '
            '--template-url=http://no.where/minimal.template '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"')

        required = [
            'stack_name',
            'id',
            'teststack2',
            '2'
        ]
        for r in required:
            self.assertRegexpMatches(create_text, r)

    def test_create_object(self):

        fakes.script_keystone_client()
        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        template_data = open(template_file).read()
        v1client.Client.raw_request(
            'GET',
            'http://no.where/container/minimal.template',
        ).AndReturn(template_data)

        resp = fakes.FakeHTTPResponse(
            201,
            'Created',
            {'location': 'http://no.where/v1/tenant_id/stacks/teststack2/2'},
            None)
        v1client.Client.json_request(
            'POST', '/stacks', body=mox.IgnoreArg(),
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))

        fakes.script_heat_list()

        self.m.ReplayAll()

        create_text = self.shell(
            'create teststack2 '
            '--template-object=http://no.where/container/minimal.template '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"')

        required = [
            'stack_name',
            'id',
            'teststack2',
            '2'
        ]
        for r in required:
            self.assertRegexpMatches(create_text, r)

    def test_update(self):
        fakes.script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            202,
            'Accepted',
            {},
            'The request is accepted for processing.')
        v1client.Client.json_request(
            'PUT', '/stacks/teststack2/2',
            body=mox.IgnoreArg(),
            headers={'X-Auth-Key': 'password', 'X-Auth-User': 'username'}
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        template_file = os.path.join(TEST_VAR_DIR, 'minimal.template')
        create_text = self.shell(
            'update teststack2/2 '
            '--template-file=%s '
            '--parameters="InstanceType=m1.large;DBUsername=wp;'
            'DBPassword=verybadpassword;KeyName=heat_key;'
            'LinuxDistribution=F17"' % template_file)

        required = [
            'stack_name',
            'id',
            'teststack2',
            '1'
        ]
        for r in required:
            self.assertRegexpMatches(create_text, r)

    def test_delete(self):
        fakes.script_keystone_client()
        resp = fakes.FakeHTTPResponse(
            204,
            'No Content',
            {},
            None)
        v1client.Client.raw_request(
            'DELETE', '/stacks/teststack2/2',
        ).AndReturn((resp, None))
        fakes.script_heat_list()

        self.m.ReplayAll()

        create_text = self.shell('delete teststack2/2')

        required = [
            'stack_name',
            'id',
            'teststack',
            '1'
        ]
        for r in required:
            self.assertRegexpMatches(create_text, r)


class ShellEnvironmentTest(TestCase):

    def setUp(self):
        super(ShellEnvironmentTest, self).setUp()
        self.m = mox.Mox()

        self.addCleanup(self.m.VerifyAll)
        self.addCleanup(self.m.UnsetStubs)

    def collect_links(self, env, content, url, map_name):
        jenv = yaml.safe_load(env)
        fields = {'files': {}}
        self.m.StubOutWithMock(urllib2, 'urlopen')
        urllib2.urlopen(url).AndReturn(cStringIO.StringIO(content))
        self.m.ReplayAll()

        v1shell._get_file_contents(jenv['resource_registry'],
                                   fields)
        self.assertEqual(fields['files'][map_name], content)

    def test_global_files(self):
        a = "A's contents."
        url = 'file:///home/b/a.yaml'
        env = '''
        resource_registry:
          "OS::Thingy": "%s"
        ''' % url
        self.collect_links(env, a, url, url)

    def test_nested_files(self):
        a = "A's contents."
        url = 'file:///home/b/a.yaml'
        env = '''
        resource_registry:
          resources:
            freddy:
              "OS::Thingy": "%s"
        ''' % url
        self.collect_links(env, a, url, url)

    def test_http_url(self):
        a = "A's contents."
        url = 'http://no.where/container/a.yaml'
        env = '''
        resource_registry:
          "OS::Thingy": "%s"
        ''' % url
        self.collect_links(env, a, url, url)

    def test_with_base_url(self):
        a = "A's contents."
        url = 'ftp://no.where/container/a.yaml'
        env = '''
        resource_registry:
          base_url: "ftp://no.where/container/"
          resources:
            server_for_me:
              "OS::Thingy": a.yaml
        '''
        self.collect_links(env, a, url, 'a.yaml')

    def test_unsupported_protocol(self):
        env = '''
        resource_registry:
          "OS::Thingy": "sftp://no.where/dev/null/a.yaml"
        '''
        jenv = yaml.safe_load(env)
        fields = {'files': {}}
        self.assertRaises(exc.CommandError,
                          v1shell._get_file_contents,
                          jenv['resource_registry'],
                          fields)
