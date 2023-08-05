import os
from distutils.core import setup


project_name = 'djeploy'
long_description = open('README').read()

# Idea from django-registration setup.py
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk(project_name):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[(len(project_name) + 1):]
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(
    name=project_name,
    version='0.2.5-dev',
    package_dir={project_name: project_name},
    packages=packages,
    package_data={project_name: data_files},
    description=\
        'Common tasks used to deploy Django powered websites via Fabric.',
    author='Peter Sanchez',
    author_email='petersanchez@gmail.com',
    license='BSD License',
    url='http://bitbucket.org/petersanchez/djeploy/',
    long_description=long_description,
    platforms=['any'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
    ],
)
