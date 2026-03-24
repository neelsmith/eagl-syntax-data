# /// script
# dependencies = [
#     "marimo",
#     "polars==1.39.3",
#     "pygithub==2.8.1",
# ]
# requires-python = ">=3.14"
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(width="columns")


@app.cell(column=0, hide_code=True)
def _(currentuser, editor, get_token, github_view, login_view, mo):
    app_disp = None
    # --- 4. MAIN APP DISPLAY ---
    if currentuser is None:
        app_disp = login_view
    elif get_token() is None:
        app_disp = github_view
    else:
        app_disp = mo.vstack([
            mo.md(f"# Syntax Editor"),
            mo.md(f"Logged in as **{currentuser}** | Connected to GitHub ✅"),
            editor

        ])

    app_disp
        # This is where your mo.ui.table and PR submission button go!
    return


@app.cell
def _(tokenseditor):
    tokenseditor
    return


@app.cell
def _():
    from io import StringIO
    import polars as pl

    return StringIO, pl


@app.cell
def _(mo, pl, tokensdf):
    relation_values = [
        "nothing",
        "subject",
        "object",
        "unit verb",
        "compound verb",
        "predicate",
        "attributive",
        "adverbial",
        "subordinating word",
    ]
    relation_columns = ["node1relation", "node2relation"]

    get_tokensdf, set_tokensdf = mo.state(tokensdf)

    def on_tokens_change(edited):
        edited_df = edited if isinstance(edited, pl.DataFrame) else pl.DataFrame(edited)
        set_tokensdf(edited_df)

    editable_columns = [
        c for c in get_tokensdf().columns if c not in relation_columns
    ]

    tokenseditor = mo.ui.data_editor(
        get_tokensdf(),
        editable_columns=editable_columns,
        on_change=on_tokens_change,
    )
    return get_tokensdf, relation_values, set_tokensdf, tokenseditor


@app.cell
def _(get_tokensdf, mo):
    row_options = {}
    _current_df = get_tokensdf()
    if _current_df.height > 0:
        if "urn" in _current_df.columns:
            row_options = {
                f"{idx + 1}: {urn}": idx
                for idx, urn in enumerate(_current_df["urn"].to_list())
            }
        else:
            row_options = {
                f"{idx + 1}": idx
                for idx in range(_current_df.height)
            }

    relation_row_choice = mo.ui.dropdown(
        options=row_options,
        label="Row to update",
    )
    return (relation_row_choice,)


@app.cell
def _(get_tokensdf, mo, relation_row_choice, relation_values):
    _selected_row = relation_row_choice.value
    node1_default = "nothing"
    node2_default = None

    if _selected_row is not None:
        _current_df = get_tokensdf()
        if 0 <= _selected_row < _current_df.height:
            _current_node1 = _current_df[_selected_row, "node1relation"]
            _current_node2 = _current_df[_selected_row, "node2relation"]
            if _current_node1 in relation_values:
                node1_default = _current_node1
            if _current_node2 in relation_values:
                node2_default = _current_node2

    relation_update_form = mo.md(
        """
        {row}

        {node1}

        {node2}
        """
    ).batch(
        row=relation_row_choice,
        node1=mo.ui.dropdown(
            options=relation_values,
            value=node1_default,
            allow_select_none=False,
            label="node1relation",
        ),
        node2=mo.ui.dropdown(
            options=relation_values,
            value=node2_default,
            allow_select_none=True,
            label="node2relation",
        ),
    ).form(submit_button_label="Apply relation values")
    return (relation_update_form,)


@app.cell
def _(get_tokensdf, pl, relation_update_form, set_tokensdf):
    relation_update_feedback = None
    if relation_update_form.value is not None:
        _selected_row = relation_update_form.value["row"]
        _node1_value = relation_update_form.value["node1"]
        _node2_value = relation_update_form.value["node2"]

        if _selected_row is None:
            relation_update_feedback = "Choose a row before applying relation values."
        elif _node1_value is None:
            relation_update_feedback = "Choose a value for node1relation before applying."
        else:
            updated_df = (
                get_tokensdf()
                .with_row_index("__row_idx")
                .with_columns(
                    pl.when(pl.col("__row_idx") == _selected_row)
                    .then(pl.lit(_node1_value))
                    .otherwise(pl.col("node1relation"))
                    .alias("node1relation"),
                    pl.when(pl.col("__row_idx") == _selected_row)
                    .then(pl.lit(_node2_value))
                    .otherwise(pl.col("node2relation"))
                    .alias("node2relation"),
                )
                .drop("__row_idx")
            )

            set_tokensdf(updated_df)
            relation_update_feedback = f"Updated relation values for row {_selected_row + 1}."
    return (relation_update_feedback,)


app._unparsable_cell(
    r"""
    value=df,
        column_config={
            "status": mo.ui.dropdown(
                options=["Todo", "Doing", "Done"],
                value="Todo" # Default for new rows
            )
    """,
    name="_"
)


@app.cell
def _(StringIO, demotokendata, pl):
    tokensdf = pl.read_csv(StringIO(demotokendata),separator="|")
    return (tokensdf,)


@app.cell
def _(tokensdf):
    tokensdf
    return


@app.cell
def _():
    demovudata = """vuid|syntactic_type|semantic_type|depth|sentence
    30pr.1.1-30pr.1.15a.1|independent clause|transitive|1|urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.1-30pr.1.15a
    30pr.1.1-30pr.1.15a.2|subordinate clause|linking|2|urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.1-30pr.1.15a
    30pr.1.1-30pr.1.15a.3|subordinate clause|transitive|2|urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.1-30pr.1.15a
    30pr.1.1-30pr.1.15a.4|subordinate clause|transitive|2|urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.1-30pr.1.15a
    """
    demotokendata="""urn|tokentype|text|verbalunit|node1|node1relation|node2|node2relation
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.1|lexical|Infans|30pr.1.1-30pr.1.15a.2|3|subject|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.2|lexical|cum|30pr.1.1-30pr.1.15a.2|nothing|nothing|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.3|lexical|esset|30pr.1.1-30pr.1.15a.2|2|unit verb|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.3a|ignore|,|0|nothing|nothing|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.4|lexical|dracones|30pr.1.1-30pr.1.15a.1|8|object|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.5|lexical|duos|30pr.1.1-30pr.1.15a.1|4|attributive|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.6|lexical|duabus|30pr.1.1-30pr.1.15a.1|7|attributive|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.7|lexical|manibus|30pr.1.1-30pr.1.15a.1|16|adverbial|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.8|lexical|necauit|30pr.1.1-30pr.1.15a.1|16|unit verb|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.8a|ignore|,|0|nothing|nothing|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.9|lexical|quos|30pr.1.1-30pr.1.15a.3|4|subordinating word|11|object
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.10|lexical|Iuno|30pr.1.1-30pr.1.15a.3|11|subject|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.11|lexical|miserat|30pr.1.1-30pr.1.15a.3|9|unit verb|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.11a|ignore|,|0|nothing|nothing|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.12|lexical|unde|30pr.1.1-30pr.1.15a.4|8|subordinating word|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.13|lexical|primigenius|30pr.1.1-30pr.1.15a.4|15|predicate|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.14|lexical|est|30pr.1.1-30pr.1.15a.4|12|unit verb|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.15|lexical|dictus|30pr.1.1-30pr.1.15a.4|14|compound verb|nothing|nothing
    urn:cts:latinLit:stoa1263.stoa001.hc_tokens:30pr.1.15a|ignore|.|0|nothing|nothing|nothing|nothing
    """
    return (demotokendata,)


@app.cell
def _():
    return


@app.cell(column=1, hide_code=True)
def _(mo):
    mo.md("""
    ## App assembly
    """)
    return


@app.cell
def _(
    mo,
    passagechoice,
    passagedisplay,
    relation_update_feedback,
    relation_update_form,
    textchoice,
    tokenseditor,
):
    relation_tools = [
        mo.md("### Relation columns"),
        mo.md("Use these dropdowns to set literal values for `node1relation` and `node2relation`."),
        relation_update_form,
    ]
    if relation_update_feedback is not None:
        relation_tools.append(mo.md(relation_update_feedback))

    editor = mo.vstack([
        mo.hstack([textchoice, passagechoice],justify="center"),
        passagedisplay,
        tokenseditor,
        mo.vstack(relation_tools),
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
    ## Syntaxing
    """)
    return


@app.cell
def _(selectedpair):
    currenturn = ""
    currentpassage = ""
    if selectedpair:
        currenturn = selectedpair[0][0]
        currentpassage = selectedpair[0][1]
    return currentpassage, currenturn


@app.cell
def _(currentpassage, currenturn, mo):
    passagedisplay = mo.vstack([mo.md(f"*Passage to analyze*: `{currenturn}`"),  mo.md(currentpassage)])
    return (passagedisplay,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Texts
    """)
    return


@app.cell
def _(mo, passages):
    passagechoice = mo.ui.dropdown(passages,label="*Passage*:")
    return (passagechoice,)


@app.cell
def _(mo, textsmenu):
    textchoice = mo.ui.dropdown(textsmenu,label="*Choose a text*:")
    return (textchoice,)


@app.cell
def _(mo):
    textsdir = mo.notebook_location() / "public" / "texts"
    return (textsdir,)


@app.cell
def _():
    textsmenu = {"Hyginus": "hyginus.cex"}
    return (textsmenu,)


@app.cell
def _(textchoice, textsdir):
    pairs = []
    if textchoice.value:
        textfile = str(textsdir / textchoice.value)
        with open(textfile, 'r', encoding='utf-8') as file:
            pairs = [line.strip().split("|") for line in file][2:]
    return (pairs,)


@app.cell
def _(pairs):
    passages = []
    baseurn = ""
    if pairs:
        passages = [pair[0].split(":")[-1] for pair in pairs]
        pieces = pairs[0][0].split(":")
        baseurn = ":".join(pieces[0:4]) + ":"
    return baseurn, passages


@app.cell
def _(baseurn, passagechoice):
    selectionurn = ""
    if passagechoice.value: 
        selectionurn = baseurn + passagechoice.value
    return (selectionurn,)


@app.cell
def _(pairs, passagechoice, selectionurn):
    selectedpair = []
    if passagechoice.value:    
        selectedpair = [pair for pair in pairs if pair[0] == selectionurn]
    return (selectedpair,)


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
