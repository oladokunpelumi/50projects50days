from setuptools import setup, find_packages

setup(
    name="twitter-reply",
    version="0.1.0",
    description="X (Twitter) AI Agent for crypto research and engagement simulation",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click==8.1.7",
        "rich==13.7.1",
        "SQLAlchemy==2.0.32",
        "python-dotenv==1.0.1",
        "openai==1.40.6",
        "requests==2.32.3",
        "pandas==2.2.2",
        "reportlab==4.2.2",
    ],
    entry_points={"console_scripts": ["twitter-reply=main:cli"]},
)
