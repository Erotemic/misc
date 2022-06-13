"""
This is a Python script to apply the PYPKG template to either create a new repo
or update an existing one with the latest standards.

TODO:
    Port logic from ~/misc/make_new_python_package_repo.sh

ComamndLine:
    python ~/misc/templates/PYPKG/apply_template.py


ExampleUsage:
    # Update my repos
    python ~/misc/templates/PYPKG/apply_template.py --repodir=$HOME/code/pyflann_ibeis --tags="erotemic,github,binpy"

    # Create this repo
    python ~/misc/templates/PYPKG/apply_template.py --repo_name=PYPKG --repodir=$HOME/code/xcookie --tags="erotemic,github,purepy"

    python ~/code/xcookie/xcookie/main.py

    /PYPKG/apply_template.py --repo_name=PYPKG --repodir=$HOME/code/xcookie --tags="erotemic,github,purepy"
"""
import toml
import shutil
import ubelt as ub
import tempfile
import scriptconfig as scfg


class TemplateConfig(scfg.Config):
    default = {
        'repodir': scfg.Value(
            None, help='path to the new or existing repo', required=True),

        'repo_name': scfg.Value(None, help='repo name'),

        'setup_secrets': scfg.Value(False),

        'tags': scfg.Value([], nargs='*', help=ub.paragraph(
            '''
            Tags modify what parts of the template are used.
            Valid tags are:
                "binpy" - do we build binpy wheels?
                "graphics" - do we need opencv / opencv-headless?
                "erotemic" - this is an erotemic repo
                "kitware" - this is an kitware repo
                "pyutils" - this is an pyutils repo
                "purepy" - this is a pure python repo
            ''')),
    }
    def normalize(self):
        if self['tags']:
            if isinstance(self['tags'], str):
                self['tags'] = [self['tags']]
            new = []
            for t in self['tags']:
                new.extend([p.strip() for p in t.split(',')])
            self['tags'] = new

    @classmethod
    def main(cls, cmdline=0, **kwargs):
        """
        Ignore:
            repodir = ub.Path('~/code/pyflann_ibeis').expand()
            kwargs = {
                'repodir': repodir,
                'tags': ['binpy', 'erotemic', 'github'],
            }
            cmdline = 0

        Example:
            repodir = ub.Path.appdir('pypkg/demo/my_new_repo')
            import sys, ubelt
            sys.path.append(ubelt.expandpath('~/misc/templates/PYPKG'))
            from apply_template import *  # NOQA
            kwargs = {
                'repodir': repodir,
            }
            cmdline = 0
        """
        import ubelt as ub
        config = TemplateConfig(cmdline=cmdline, data=kwargs)
        repo_dpath = ub.Path(config['repodir'])
        repo_dpath.ensuredir()

        IS_NEW_REPO = 0

        create_new_repo_info = ub.codeblock(
            '''
            # TODO:
            # At least instructions on how to create a new repo, or maybe an
            # API call
            https://github.com/new

            git init
            ''')
        print(create_new_repo_info)

        if IS_NEW_REPO:
            # TODO: git init
            # TODO: github or gitlab register
            pass

        self = TemplateApplier(config)
        self.setup().gather_tasks()

        self.setup().apply()

        if config['setup_secrets']:
            setup_secrets_fpath = self.repo_dpath / 'dev/setup_secrets.sh'
            if 'erotemic' in self.config['tags']:
                environ_export = 'setup_package_environs_github_erotemic'
                upload_secret_cmd = 'upload_github_secrets'
            elif 'pyutils' in self.config['tags']:
                environ_export = 'setup_package_environs_github_pyutils'
                upload_secret_cmd = 'upload_github_secrets'
            elif 'kitware' in self.config['tags']:
                environ_export = 'setup_package_environs_gitlab_kitware'
                upload_secret_cmd = 'upload_gitlab_repo_secrets'
            else:
                raise Exception

            import cmd_queue
            script = cmd_queue.Queue.create()
            script.submit(ub.codeblock(
                f'''
                cd {self.repo_dpath}
                source {setup_secrets_fpath}
                {environ_export}
                load_secrets
                export_encrypted_code_signing_keys
                git commit -am "Updated secrets"
                {upload_secret_cmd}
                '''))
            script.rprint()


class TemplateApplier:

    def _build_template_registry(self):
        """
        Take stock of the files in the template repo and ensure they all have
        appropriate properties.
        """
        self.template_infos = [
            # {'template': 1, 'overwrite': False, 'fname': '.circleci/config.yml'},
            # {'template': 1, 'overwrite': False, 'fname': '.travis.yml'},

            {'template': 0, 'overwrite': 1, 'fname': 'publish.sh'},
            {'template': 0, 'overwrite': 1, 'fname': 'dev/setup_secrets.sh'},

            {'template': 0, 'overwrite': 0, 'fname': '.gitignore'},
            # {'template': 1, 'overwrite': 1, 'fname': '.coveragerc'},
            {'template': 0, 'overwrite': 1, 'fname': '.readthedocs.yml'},
            # {'template': 0, 'overwrite': 1, 'fname': 'pytest.ini'},
            {'template': 0, 'overwrite': 1, 'fname': 'pyproject.toml', 'dynamic': 'build_pyproject'},

            {'template': 0, 'overwrite': 1, 'fname': '.github/dependabot.yml', 'tags': 'github'},
            {'template': 0, 'overwrite': 1, 'fname': '.github/workflows/test_binaries.yml', 'tags': 'binpy,github'},
            {'template': 1, 'overwrite': 1, 'fname': '.github/workflows/tests.yml', 'tags': 'purepy,github'},

            {'template': 1, 'overwrite': 1, 'fname': '.gitlab-ci.yml', 'tags': 'gitlab'},
            # {'template': 1, 'overwrite': False, 'fname': 'appveyor.yml'},
            {'template': 1, 'overwrite': 0, 'fname': 'CMakeLists.txt', 'tags': 'binpy'},
            {'template': 1, 'overwrite': 0, 'fname': 'README.rst'},

            {'template': 0, 'overwrite': 1, 'fname': 'dev/make_strict_req.sh'},
            {'template': 0, 'overwrite': 1, 'fname': 'requirements.txt'},  # 'dynamic': 'build_requirements'},
            {'template': 0, 'overwrite': 0, 'fname': 'requirements/graphics.txt', 'tags': 'graphics'},
            {'template': 0, 'overwrite': 0, 'fname': 'requirements/headless.txt', 'tags': 'graphics'},
            {'template': 0, 'overwrite': 0, 'fname': 'requirements/optional.txt'},
            {'template': 0, 'overwrite': 0, 'fname': 'requirements/runtime.txt'},
            {'template': 0, 'overwrite': 0, 'fname': 'requirements/tests.txt'},

            {'template': 1, 'overwrite': 1, 'fname': 'run_doctests.sh'},
            {'template': 1, 'overwrite': 1, 'fname': 'build_wheels.sh'},
            {'template': 1, 'overwrite': 1, 'fname': 'run_tests.py'},
            {'template': 1, 'overwrite': 0, 'fname': 'setup.py'},
        ]
        if 0:
            # Checker and help autopopulate
            import os
            template_contents = []
            dname_blocklist = {
                '__pycache__',
                'old',
                '.circleci',
            }
            fname_blocklist = {
                'apply_template.py',
                'install_template.sh',
                '.travis.yml',
            }
            for root, ds, fs in self.template_dpath.walk():
                for d in set(ds) & dname_blocklist:
                    ds.remove(d)
                fs = set(fs) - fname_blocklist
                if fs:
                    rel_root = root.relative_to(self.template_dpath)
                    for fname in fs:
                        abs_fpath = root / fname
                        is_template = int('PYPKG' in abs_fpath.read_text())
                        rel_fpath = rel_root / fname
                        # overwrite indicates if we dont expect the user to
                        # make modifications
                        template_contents.append({
                            'template': is_template,
                            'overwrite': False,
                            'fname': os.fspath(rel_fpath),
                        })
            print('template_contents = {}'.format(ub.repr2(sorted(template_contents, key=lambda x: x['fname']), nl=1, sort=0)))
            known_fpaths = {d['fname'] for d in self.template_infos}
            exist_fpaths = {d['fname'] for d in template_contents}
            unexpected_fpaths = exist_fpaths - known_fpaths
            if unexpected_fpaths:
                print(f'WARNING UNREGISTERED unexpected_fpaths={unexpected_fpaths}')

    def __init__(self, config):
        self.config = config
        self.repo_dpath = ub.Path(self.config['repodir'])
        if self.config['repo_name'] is None:
            self.config['repo_name'] = self.repo_dpath.name
        self.repo_name = self.config['repo_name']
        self._tmpdir = tempfile.TemporaryDirectory(prefix=self.repo_name)

        self.template_infos = None
        self.template_dpath = ub.Path('~/misc/templates/PYPKG').expand()
        self.staging_dpath = ub.Path(self._tmpdir.name)

    def setup(self):
        self._build_template_registry()
        self.stage_files()
        return self

    def stage_files(self):
        import xdev
        self.staging_infos = []
        for info in ub.ProgIter(self.template_infos, desc='staging'):
            tags = info.get('tags', None)
            if tags:
                tags = set(tags.split(','))
                if not set(self.config['tags']).issuperset(tags):
                    continue
            stage_fpath = self.staging_dpath / info['fname']
            if info.get('dynamic', ''):
                text = getattr(self, info.get('dynamic', ''))()
                stage_fpath.write_text(text)
            else:
                raw_fpath = self.template_dpath / info['fname']
                stage_fpath.parent.ensuredir()
                shutil.copy2(raw_fpath, stage_fpath)
                if info['template']:
                    xdev.sedfile(stage_fpath, 'PYPKG', self.repo_name, verbose=0)

            info['stage_fpath'] = stage_fpath
            info['repo_fpath'] = self.repo_dpath / info['fname']
            self.staging_infos.append(info)

        if 1:
            import pandas as pd
            df = pd.DataFrame(self.staging_infos)
            print(df)

    def gather_tasks(self):
        tasks = {
            'copy': []
        }
        stats = {
            'missing': [],
            'dirty': [],
            'clean': [],
        }
        import xdev
        for info in self.staging_infos:
            stage_fpath = info['stage_fpath']
            repo_fpath = info['repo_fpath']
            if not repo_fpath.exists():
                stats['missing'].append(repo_fpath)
                tasks['copy'].append((stage_fpath, repo_fpath))
                print(f'Does not exist repo_fpath={repo_fpath}')
            elif info['overwrite']:
                print(f'repo_fpath={repo_fpath}')
                assert stage_fpath.exists()
                repo_text = repo_fpath.read_text()
                stage_text = stage_fpath.read_text()
                if stage_text.strip() == repo_text.strip():
                    difftext = None
                else:
                    difftext = xdev.difftext(repo_text, stage_text, colored=1)
                if difftext:
                    tasks['copy'].append((stage_fpath, repo_fpath))
                    stats['dirty'].append(repo_fpath)
                    print(difftext)
                else:
                    stats['clean'].append(repo_fpath)
        print('stats = {}'.format(ub.repr2(stats, nl=2)))
        return stats, tasks

    def apply(self):
        stats, tasks = self.gather_tasks()

        copy_tasks = tasks['copy']
        if copy_tasks:
            from rich.prompt import Confirm
            flag = Confirm.ask('Do you want to apply this patch?')
            if flag:
                dirs = {d.parent for s, d in copy_tasks}
                for d in dirs:
                    d.ensuredir()
                for src, dst in copy_tasks:
                    shutil.copy2(src, dst)

    # def build_requirements(self):
    #     pass

    def build_pyproject(self):
        # data = toml.loads((self.template_dpath / 'pyproject.toml').read_text())
        # print('data = {}'.format(ub.repr2(data, nl=5)))
        pyproj_config = ub.AutoDict()
        # {'tool': {}}
        if 'binpy' in self.config['tags']:
            pyproj_config['build-system']['requires'] = [
                "setuptools>=41.0.1",
                # setuptools_scm[toml]
                "wheel",
                "scikit-build>=0.9.0",
                "numpy",
                "ninja"
            ]
            pyproj_config['tool']['cibuildwheel'].update({
                'build': "cp37-* cp38-* cp39-* cp310-*",
                'build-frontend': "build",
                'skip': "pp* cp27-* cp34-* cp35-* cp36-* *-musllinux_*",
                'build-verbosity': 1,
                'test-requires': ["-r requirements/tests.txt"],
                'test-command': "python {project}/run_tests.py"
            })

            if True:
                cibw = pyproj_config['tool']['cibuildwheel']
                req_commands = {
                    'linux': [
                        'yum install epel-release lz4 lz4-devel -y',
                    ],
                    'windows': [
                        'choco install lz4 -y',
                    ],
                    'macos': [
                        'brew install lz4',
                    ]
                }
                for plat in req_commands.keys():
                    cmd = ' && '.join(req_commands[plat])
                    cibw[plat]['before-all'] = cmd

        WITH_PYTEST_INI = 1
        if WITH_PYTEST_INI:
            pytest_ini_opts = pyproj_config['tool']['pytest']['ini_options']
            pytest_ini_opts['addopts'] = "-p no:doctest --xdoctest --xdoctest-style=google --ignore-glob=setup.py"
            pytest_ini_opts['norecursedirs'] = ".git ignore build __pycache__ dev _skbuild"
            pytest_ini_opts['filterwarnings'] = [
                "default",
                "ignore:.*No cfgstr given in Cacher constructor or call.*:Warning",
                "ignore:.*Define the __nice__ method for.*:Warning",
                "ignore:.*private pytest class or function.*:Warning",
            ]

        WITH_COVERAGE = 1
        if WITH_COVERAGE:
            pyproj_config['tool']['coverage'].update(toml.loads(ub.codeblock(
                '''
                [run]
                branch = true

                [report]
                exclude_lines =[
                    "pragma: no cover",
                    ".*  # pragma: no cover",
                    ".*  # nocover",
                    "def __repr__",
                    "raise AssertionError",
                    "raise NotImplementedError",
                    "if 0:",
                    "if trace is not None",
                    "verbose = .*",
                    "^ *raise",
                    "^ *pass *$",
                    "if _debug:",
                    "if __name__ == .__main__.:",
                    ".*if six.PY2:"
                ]

                omit=[
                    "{REPO_NAME}/__main__.py",
                    "*/setup.py"
                ]
                ''').format(REPO_NAME=self.repo_name)))

        text = toml.dumps(pyproj_config)
        return text


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/templates/PYPKG/apply_template.py --help
    """
    TemplateConfig.main(cmdline={
        'strict': True,
        'autocomplete': True,
    })
