# Project Setup Guide for Backend side

This guide will help you set up and run the IndustryPromptEnhancer app for the backend side.

## Project Structure

```
project/
├── .vscode/
│   ├── launch.json
│   └── tasks.json
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── workflow.py
│   │   ├── tools.py
│   │   └── models.py
│   ├── venv/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
└── env/
    ├── .env.local
```

---

## Prerequisites

### Requirements

- Python 3.13
- VS Code with Python extension installed
- [debugpy](https://pypi.org/project/debugpy/) for debugging
- uvicorn server
- [mkcert](https://github.com/FiloSottile/mkcert) for generating local certificates for making request to the backend using HTTPS

---

## Setup Instructions

### Prerequisites Installation:

1. Open PowerShell as Administrator

2. Install Python:

```bash

# Check if Chocolatey is installed (package manager)
# If not, install it first
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python (as example we use 3.13.3 version)
choco install python --version=3.13.3

```

3. Install [mkcert](https://github.com/FiloSottile/mkcert) for generating local certificates for HTTPS requests

```bash

# Install mkcert locally
## On Windows (using chocolatey):
choco install mkcert

## On macOS:
brew install mkcert

# Install local CA (locally)
mkcert -install

```

in the backend folder `IndustryPromptEnhancer\backend`

```bash

# Generate certificate for localhost (`IndustryPromptEnhancer\backend`)
...\IndustryPromptEnhancer\backend> mkcert localhost

```

4. Define environment variables.

If the `.env.local` file does not exist in the `env` folder, create it.

Add the following:

```json
# Frontend
.....

# Backend

```

## VS Code Setup:

- Open VS Code
- Install Extensions:

  - Python (by Microsoft)
  - Python Extension Pack
  - Pylance
  - Azure Tools

---

## Create virtual environment and install dependencies:

1. Create virtual environment

```bash
cd backend
python -m venv venv
```

2. Activate virtual environment

```bash

# Windows
...\IndustryPromptEnhancer\backend> venv\Scripts\activate

```

**NOTE:**

> If you encounter the following error: _backend\venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at https:/go.microsoft.com/fwlink/?LinkID=135170_
>
> Follow these steps:
>
> 1. Open PowerShell as Administrator:
>    Press Win + X and choose "Windows PowerShell (Admin)" or search for PowerShell, right-click, and select "Run as administrator".
>
> 2. Change the Execution Policy:
>    To allow scripts to run, execute the following command:
>
> ```bash
>   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> When prompted, type `Y` and press `Enter` to confirm the change.
>
> Explanation:
> RemoteSigned allows scripts created on your local computer to run without a signature, while scripts downloaded from the internet must be signed by a trusted publisher.

3. Setting up intellisense:

3.1 Find Python installation path:

1.  Open Terminal _(e.g. Windows PowerShell)_ as Administrator
2.  In the Terminal window, type the following command:

```bash
(Get-Command python).Path
```

Example:

```bash
PS C:\Users> (Get-Command python).Path

# Example of the path where Python is installed
C:\Python311\python.exe
```

As an alternative you can try typing the following in `cmd`:

```bash
# Windows
where python

# macOS/Linux
which python
```

3.2. In VS Code:

1. Open settings
2. Extensions
3. Python
4. Default Interpreter Path
5. Paste the full path to your Python installation folder or the `python.exe` file.
   For example: `C:\Python313` or `C:\Python313\python.exe`

**NOTE:** If it didn't work immediately, try reloading VS Code.

For more info please refer to [Python environments in VS Code](https://code.visualstudio.com/docs/python/environments)

4. Specify Interpreter
   Find interpreter in the created virtual environment. It should be in `venv/Scripts` folder that is `venv/Scripts/python.exe`
   in VSCode click `Ctrl`+`Shift`+`P` and write `Select Interpreter` select `Python: Select Interpreter`. Select the `Enter interpreter path...` option that shows on the top of the interpreters list.

![Enter Interpreter Path](./images/enter-interpreter-path.png)

Select the `Find...` button and browse to `venv/Scripts` folder and choose `python.exe`

![Find Interpreter](./images/enter-or-find-interpreter.png)

5. Install dependencies

> If the virutal environment is activated the path should be prefixed
> with `(venv)`
>
> Example: _`(venv) ...\IndustryPromptEnhancer\backend>`_

After activating virtual environment, run the following in terminal
_(in `IndustryPromptEnhancer\backend`)_

```bash
(venv) ...\IndustryPromptEnhancer\backend> pip install -r requirements.txt
```

**NOTE:**
Below are some common commands for working with `requirements.txt`

### Install the Package

```bash
(venv) ...\IndustryPromptEnhancer\backend> pip install <package-name>
```

### Generate or Update `requirements.txt`

1. Using pip freeze:

The pip freeze command outputs the installed packages and their versions in a format suitable for `requirements.txt`.

Run the following command in your terminal:

```bash
(venv) ...\IndustryPromptEnhancer\backend> pip freeze > requirements.txt
```

2. Manually Adding to `requirements.txt`:

To manually add the package, open `requirements.txt` file in a text editor.

Add the following line with the version you installed:

```bash
(venv) ...\IndustryPromptEnhancer\backend> <package-name>==<version>
```

Replace `<version>` with the version number of <package-name> that was installed.
You can find the installed version by running:

```bash
(venv) ...\IndustryPromptEnhancer\backend> pip show <package-name>
```

3. Verify `requirements.txt`

Open the `requirements.txt` file and verify that <package-name> is listed with the correct version.

The file should look something like this:

```
<package-name>==<version>
# Other dependencies...
```

### Install Dependencies from `requirements.txt`

To install all the dependencies listed in `requirements.txt`, run:

```bash
(venv) ...\IndustryPromptEnhancer\backend> pip install -r requirements.txt
```

---

## Debugging

- Breakpoints can be set directly in VS Code
- Debug configuration uses `debugpy`
- Server auto-reloads on code changes

---

## Environment Configuration

- Backend environment variables are loaded from the Python environment

---

## Common Issues

1. **Port Already in Use**

   - Check if another instance is running
   - Change port in launch configuration

2. **Module Not Found**

   - Ensure virtual environment is activated
   - Verify all dependencies are installed
   - Check cwd in launch.json

---

Additional Links:

https://code.visualstudio.com/docs/python/environments

https://code.visualstudio.com/docs/python/debugging#_set-configuration-options

https://code.visualstudio.com/docs/python/editing
