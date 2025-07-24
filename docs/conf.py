from instrumentman import __version__


project = "Instrumentman"
copyright = "2025, MrClock8163"
author = "MrClock8163"

version = ".".join(__version__.split(".")[0:2])
release = __version__

extensions = [
    "notfound.extension",
    "sphinx_last_updated_by_git",
    "sphinx_immaterial",
    "sphinx_mdinclude",
    "sphinx_click"
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
templates_path = ["_templates"]
sphinx_immaterial_icon_path = ["_templates/.icons"]
sphinx_immaterial_override_generic_admonitions = False
sphinx_immaterial_override_builtin_admonitions = False
sphinx_immaterial_override_version_directives = False
sphinx_immaterial_generate_extra_admonitions = False

html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]
html_logo = "_static/logo.svg"
html_favicon = "_static/favicon.svg"
html_last_updated_fmt = "%d %b %Y"
html_copy_source = False
html_scaled_image_link = False
html_use_opensearch = "https://instrumentman.readthedocs.io"
html_theme = 'sphinx_immaterial'
html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
        "edit": "material/file-edit-outline",
    },
    "features": [
        "content.code.copy",
        "navigation.top",
        "navigation.sections",
        "navigation.expand",
        "navigation.path",
        "toc.follow"
    ],
    "site_url": "https://instrumentman.readthedocs.io",
    "repo_url": "https://github.com/MrClock8163/Instrumentman",
    "repo_name": "Instrumentman",
    "palette": [
        {
            "media": "(prefers-color-scheme)",
            "toggle": {
                "icon": "material/brightness-auto",
                "name": "Switch to light mode",
            },
        },
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "custom",
            "accent": "custom",
            "toggle": {
                "icon": "material/weather-sunny",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "custom",
            "accent": "custom",
            "toggle": {
                "icon": "material/weather-night",
                "name": "Switch to system preference",
            },
        },
    ],
    "social": [
        {
            "icon": "fontawesome/brands/github",
            "link": "https://github.com/MrClock8163/Instrumentman",
            "name": "Project on GitHub"
        },
        {
            "icon": "fontawesome/brands/python",
            "link": "https://pypi.org/project/instrumentman/",
        }
    ]
}

# Error checking
nitpicky = True

latex_documents = [
    (
        "latexindex", "instrumentman.tex",
        "Instrumentman documentation", "MrClock8163",
        "manual", False
    )
]
latex_logo = "iman_logo.png"
latex_elements = {
    "papersize": "a4paper",
    "extraclassoptions": "oneside",
    "makeindex": (
        r"\usepackage[columns=1]{idxlayout}"
        r"\makeindex"
    ),
    "preamble": (
        r"\usepackage{titlesec}"
        r"\newcommand{\sectionbreak}{\clearpage}"
        r"\setcounter{tocdepth}{2}"
        r"\definecolor{vadded}{RGB}{54,145,0}"
        r"\definecolor{vchanged}{RGB}{228,160,1}"
        r"\definecolor{vremoved}{RGB}{204,0,0}"
        r"\newcommand{\DUroleversionmodified}[1]{\textit{\textbf{#1}}}"
        r"\newcommand{\DUroleadded}{\color{vadded}}"
        r"\newcommand{\DUrolechanged}{\color{vchanged}}"
        r"\newcommand{\DUroleremoved}{\color{vremoved}}"
        r"\newcommand{\DUroledeprecated}{\color{vremoved}}"
    ),
    "fontpkg": (
        r"\usepackage{lmodern}"
        r"\renewcommand*{\familydefault}{\rmdefault}"
        r"\renewcommand{\ttdefault}{lmtt}"
    ),
    # https://www.sphinx-doc.org/en/master/latex.html#additional-css-like-sphinxsetup-keys
    "sphinxsetup": ", ".join(
        map(
            lambda p: f"div.{p}_border-radius=3pt",
            (
                "attention",
                "caution",
                "danger",
                "error",
                "hint",
                "important",
                "note",
                "tip",
                "warning",
                "seealso"
            )
        )
    )
}
