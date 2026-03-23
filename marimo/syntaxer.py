# /// script
# dependencies = [
#     "marimo",
#     "pygithub==2.8.1",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(width="columns")


@app.cell(column=0)
def _(currentuser, editor, get_token, github_view, login_view, mo):
    app_disp = None
    # --- 4. MAIN APP DISPLAY ---
    if currentuser is None:
        app_disp = login_view
    elif get_token() is None:
        app_disp = github_view
    else:
        app_disp = mo.vstack([
            mo.md(f"# 🚀 Data Editor Active"),
            mo.md(f"Logged in as **{currentuser}** | Connected to GitHub ✅"),
            editor
        
        ])

    app_disp
        # This is where your mo.ui.table and PR submission button go!
    return


@app.cell(column=1, hide_code=True)
def _(mo):
    mo.md("""
    ## App assembly
    """)
    return


@app.cell
def _(mo, textchoice):
    editor = mo.vstack([
        textchoice
    ])
    return (editor,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Imports
    """)
    return


@app.cell
def _():
    import marimo as mo
    import hashlib
    from github import Github

    return Github, hashlib, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Texts
    """)
    return


@app.cell
def _(mo):
    textsdir = mo.notebook_location() / "public" / "texts"
    return (textsdir,)


@app.cell
def _():
    textsmenu = {"Hyginus": "hyginus.cex"}
    return (textsmenu,)


@app.cell
def _(mo, textsmenu):
    textchoice = mo.ui.dropdown(textsmenu,label="*Choose a text*:")
    return (textchoice,)


@app.cell
def _(textchoice, textsdir):
    textfile = None
    if textchoice.value:
        f = textsdir / textchoice.value
    return (f,)


@app.cell
def _(f):
    f
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Authentication
    """)
    return


@app.cell
def _(get_user):
    currentuser = get_user()
    return (currentuser,)


@app.cell
def _(mo):
    # --- 1. SETUP & STATE ---
    # Mock user registry (In production, load this from your users.json)
    USER_REGISTRY = {"admin": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"}

    get_user, set_user = mo.state(None)
    get_token, set_token = mo.state(None)
    return USER_REGISTRY, get_token, get_user, set_token, set_user


@app.cell
def _(mo):
    login_form = mo.md(
        """
        ## 👤 Step 1: App Login

        {username}

        {password}
        """
    ).batch(
        username=mo.ui.text(label="App Username"),
        password=mo.ui.text(label="App Password", kind="password"),
    ).form(submit_button_label="Log In")
    return (login_form,)


@app.cell
def _(USER_REGISTRY, hashlib, login_form, mo, set_user):
    login_feedback = None
    if login_form.value is not None:
        username = login_form.value["username"]
        password = login_form.value["password"]
        hashed = hashlib.sha256(password.encode()).hexdigest()
        if USER_REGISTRY.get(username) == hashed:
            set_user(username)
            login_feedback = mo.md("🔓 Login Successful!")
        else:
            login_feedback = mo.md("❌ Invalid credentials.")
    return (login_feedback,)


@app.cell
def _(login_feedback, login_form, mo):
    login_items = [login_form]
    if login_feedback is not None:
        login_items.append(login_feedback)
    login_view = mo.vstack(login_items)
    return (login_view,)


@app.cell
def _(mo):
    github_form = mo.md(
        """
        {token}
        """
    ).batch(
        token=mo.ui.text(label="Paste your GitHub Token here", kind="password"),
    ).form(submit_button_label="Verify & Connect")
    return (github_form,)


@app.cell
def _(Github, github_form, mo, set_token):
    verification_status = None
    if github_form.value is not None:
        try:
            token = github_form.value["token"]
            g = Github(token)
            github_user = g.get_user().login
            set_token(token)
            verification_status = mo.md(f"✅ **Linked to GitHub as {github_user}!**")
        except Exception:
            verification_status = mo.md("❌ **Invalid Token.** Check the guide above.")
    return (verification_status,)


@app.cell
def _(currentuser, github_form, mo, verification_status):
    guide = mo.accordion({
        "❓ How do I get a GitHub Token?": mo.vstack([
            mo.md("1. Open [GitHub Token Settings](https://github.com/settings/tokens/new) (Classic)."),
            mo.md("2. Set **Note** to 'Data Editor'."),
            mo.md("3. **Crucial:** Check the box for **'repo'**."),
            mo.md("4. Click **Generate Token** at the bottom and copy the code."),
        ])
    })

    github_items = [
        mo.md(f"## 🛠️ Step 2: Connect GitHub (User: {currentuser})"),
        guide,
        github_form,
    ]
    if verification_status is not None:
        github_items.append(verification_status)

    github_view = mo.vstack(github_items)
    return (github_view,)


if __name__ == "__main__":
    app.run()
