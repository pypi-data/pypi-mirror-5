from setuptools import setup, find_packages

version = '4.2'

setup(
    name='django-bower',
    version=version,
    description="Integrate django with bower",
    long_description="""\
    Easy way to use bower with your django project
""",
    classifiers=[
        'Framework :: Django',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    keywords='',
    author='Vladimir Iakovlev',
    author_email='nvbn.rm@gmail.com',
    url='https://github.com/nvbn/django-bower',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'example', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'django',
        'mock',
        'six',
    ],
    entry_points="""
      # -*- Entry points: -*-
      """,
)
