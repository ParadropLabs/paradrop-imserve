from setuptools import find_packages, setup

setup(name="paradrop-imserve",
      version="0.1",
      description="Virtual camera that serves images in a sequence.",
      author="Paradrop Labs",
      author_email="info@paradrop.io",
      url="https://paradrop.org",
      packages=find_packages(),
      install_requires=[
          "Flask==1.0.2",
          "requests==2.19.1"
      ],
      entry_points={
          "console_scripts": [
              "paradrop-imserve = imserve.server:main"
          ]
      }
)
