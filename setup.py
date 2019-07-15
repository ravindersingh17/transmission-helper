from setuptools import setup

setup(
        name="torhelp",
        version="1.1",
        description="Media Download Helper",
        author="Ravi",
        author_email="n30.2006@gmail.com",
        install_requires=["requests", "transmissionrpc", "bs4"],
        packages=["torhelp"],
        scripts=["tor-cli"],
        python_requires=">=3",
        )

