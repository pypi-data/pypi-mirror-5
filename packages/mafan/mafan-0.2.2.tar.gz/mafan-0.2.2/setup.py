from distutils.core import setup

setup(
    name='mafan',
    version='0.2.2',
    author='Herman Schaaf',
    author_email='herman@ironzebra.com',
    packages=['mafan', 'mafan.hanzidentifier'],
    scripts=['bin/convert.py'],
    url='https://github.com/hermanschaaf/mafan',
    license='LICENSE.txt',
    description='A toolbox for working with the Chinese language in Python',
    long_description=open('docs/README.md').read(),
    install_requires=[
        "jieba == 0.29",
        "argparse == 1.2.1",
        "chardet == 2.1.1",
        "wsgiref == 0.1.2",
        "jianfan == 0.0.1",
    ],
)