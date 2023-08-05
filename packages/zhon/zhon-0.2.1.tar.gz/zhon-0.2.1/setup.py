from setuptools import setup
import sys

if sys.version_info < (3, ):
    import codecs
    enc_open = codecs.open
else:
    enc_open = open


with enc_open('README.rst', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='zhon',
    version='0.2.1',
    author='Thomas Roten',
    author_email='thomas@roten.us',
    url='https://github.com/tsroten/zhon',
    description=('Zhon provides constants used in Chinese text processing.'),
    long_description=long_description,
    packages=['zhon', 'zhon.cedict'],
    keywords=('chinese mandarin segmentation tokenization punctuation hanzi '
              'unicode radicals han cjk cedict cc-cedict traditional '
              'simplified characters pinyin zhuyin'),
    classifiers=[
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
    ],
    platforms='Any',
)
