from setuptools import setup

if __name__ == "__main__":
    setup(
        name="ikea_api",
        install_requires=[
            "requests==2.26.0",
            "typing-extensions==4.0.0; python_version < '3.9'",
        ],
        extras_require={
            "dev": [
                "black==21.9b0",
                "pre-commit==2.15.0",
            ],
            "test": [
                "pytest==6.2.5",
                "pytest-cov==3.0.0",
                "pytest-randomly==3.10.1",
                "responses==0.15.0",
            ],
        },
    )
