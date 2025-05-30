from setuptools import setup, find_packages

setup(
    name="deepl-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask==3.0.2",
        "flask-cors==4.0.0",
        "langdetect==1.0.9",
        "pyttsx3==2.90",
        "requests==2.31.0",
        "numpy==1.26.4",
        "python-dotenv==1.0.1",
        "pytest==8.0.0",
        "pytest-cov==4.1.0",
    ],
) 