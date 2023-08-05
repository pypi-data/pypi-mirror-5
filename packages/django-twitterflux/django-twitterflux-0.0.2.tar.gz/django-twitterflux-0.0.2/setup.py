from setuptools import setup, find_packages
setup(
    name="django-twitterflux",
    version="0.0.2",
    packages=find_packages(),
    author="sergio Garcez",
    author_email="garcez.sergio@gmail.com",
    description="Retrieval and storage of recent tweets in Django.",
    url="https://github.com/sgarcez/django-twitter-flux/",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "python-twitter >= 0.8.7",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python',
    ]
)
