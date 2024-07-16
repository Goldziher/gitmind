<p align="center">
  <!-- github-banner-start -->
  <img src="https://github.com/Goldziher/gitmind/blob/main/assets/logo_white_bg.svg?raw=true" alt="GitMind Logo - Light" width="100%" height="auto" />
  <!-- github-banner-end -->
</p>

# Gitmind

AI powered Git repository analysis and reporting.

This project is currently in its infancy. The readme will be updated to include more information as the project progresses.

If you find what you are seeing intriguing, go ahead and ⭐️ the repository to show your support.

## Local Development

### Prerequisites

- A compatible python version. It's recommended to use [pyenv](https://github.com/pyenv/pyenv) to manage
python versions.
- [pdm](https://github.com/pdm-project/pdm) installed.
- [pre-commit](https://pre-commit.com) installed.
- [hatch](https://hatch.pypa.io) installed,

### Setup

1. Clone the repository
3. Inside the repository, install the dependencies with:
   ```shell
      pdm install
   ```
   This will create a virtual env under the git ignored `.venv` folder and install all the dependencies.
3. Install the pre-commit hooks:
   ```shell
      pre-commit install && pre-commit install --hook-type commit-msg
   ```
   This will install the pre-commit hooks that will run before every commit. This includes linters and formatters.

### Linting

To lint the codebase, run:
```shell
   pdm run lint
```

### Testing

To run the tests, run:
```shell
   pdm run test
```

Tip: You can also run the linters configured in `pyproject.toml` inside your IDE of choice.
