% ============================================================================
% aifrontiers.cls
% LaTeX class for Microsoft AI Frontiers technical reports
% ============================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{aifrontiers}[2025/05/15 v2.0 AI Frontiers report class]

% ---------------------------------------------------------------------------
% Base class + option handling
% ---------------------------------------------------------------------------
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass{article}

% ---------------------------------------------------------------------------
% Packages
% ---------------------------------------------------------------------------
\RequirePackage{newtxtext}
\RequirePackage{amsmath}
\RequirePackage{newtxmath}
\RequirePackage{graphicx}
\RequirePackage{microtype}
\RequirePackage{setspace}
\RequirePackage{xcolor}
\RequirePackage{url}
\RequirePackage{hyperref}
\RequirePackage{fancyhdr}
\RequirePackage{natbib}
\RequirePackage[letterpaper,margin=2.5cm,headheight=24pt]{geometry}
\RequirePackage{environ}
\RequirePackage{etoolbox}
\RequirePackage[skins,breakable]{tcolorbox}

% ---------------------------------------------------------------------------
% Colors
% ---------------------------------------------------------------------------
\definecolor{darkblue}{rgb}{0, 0, 0.6}
\definecolor{aifrontiersblue}{HTML}{0050EF}
\definecolor{aifrontiersgrey}{RGB}{80,80,80}

% Title block style controls.
\newcommand{\AIFTitleTopGap}{0pt}
\newcommand{\AIFTitleAuthorGap}{1.4em}

% Abstract box style controls. Adjust these values without editing \maketitle.
% Strength values range from 0 (white) to 100 (full base purple).
\definecolor{aifrontiersabstractpurple}{HTML}{A986CF}
\newcommand{\AIFAbstractBackgroundStrength}{25}
\newcommand{\AIFAbstractFrameStrength}{60}
\newcommand{\AIFAbstractBoxRule}{0.7pt}
\newcommand{\AIFAbstractArc}{4pt}
\newcommand{\AIFAbstractSidePadding}{8pt}
\newcommand{\AIFAbstractVerticalPadding}{6pt}
\newcommand{\AIFAbstractTopGap}{35pt}
\newcommand{\AIFAbstractBottomGap}{10pt}
\newcommand{\AIFAbstractTitleSize}{\large}
\newcommand{\AIFAbstractTitleGap}{2pt}

% ---------------------------------------------------------------------------
% Hyperref + natbib setup
% ---------------------------------------------------------------------------
\hypersetup{
  colorlinks=true,
  linkcolor=darkblue,
  citecolor=aifrontiersblue,
  urlcolor=darkblue,
}
\setcitestyle{authoryear,round,citesep={;},aysep={,},yysep={;}}

% ---------------------------------------------------------------------------
% Spacing
% ---------------------------------------------------------------------------
\setlength{\parskip}{6pt}
\setlength{\parindent}{0pt}
\onehalfspacing

% ---------------------------------------------------------------------------
% Header / footer (short title on every page)
% ---------------------------------------------------------------------------
\newcommand{\AIFShortTitle}{}%
\newcommand{\shorttitle}[1]{\gdef\AIFShortTitle{#1}}%
\newcommand{\AIFDisplayShortTitle}{%
  \ifx\AIFShortTitle\@empty
    \@title
  \else
    \AIFShortTitle
  \fi
}

\newcommand{\AIFLogo}{%
  \raisebox{-0.1ex}{\includegraphics[height=1.5em]{logo/MatrAIx-logo-PureText-black-vectorized.pdf}}%
}

\pagestyle{fancy}
\fancyhf{}%
\renewcommand{\headrulewidth}{1pt}
\renewcommand{\headrule}{%
  {\color[HTML]{4D4D4D}\hrule\@height\headrulewidth\@width\headwidth\vskip-\headrulewidth}%
}
\fancyhead[L]{\sffamily\small\bfseries\AIFDisplayShortTitle}
\fancyhead[R]{\sffamily\small\thepage}

\fancypagestyle{firstpage}{%
  \fancyhf{}%
  \fancyhead[L]{\AIFLogo\hspace{1em}}%
  \fancyhead[R]{\sffamily\small\@date}%
  \renewcommand{\headrulewidth}{1pt}%
  \renewcommand{\headrule}{%
    {\color[HTML]{4D4D4D}\hrule\@height\headrulewidth\@width\headwidth\vskip-\headrulewidth}%
  }%
}

% ---------------------------------------------------------------------------
% Abstract handling (captured and rendered in box)
% ---------------------------------------------------------------------------
\newcommand{\abstracttext}{}%
\RenewEnviron{abstract}{%
  \global\let\abstracttext\BODY
}

% ---------------------------------------------------------------------------
% Link block above abstract
% ---------------------------------------------------------------------------
\providecommand{\hflink}{}%
\providecommand{\weblink}{}%
\providecommand{\ghlink}{}%
\providecommand{\foundrylink}{}

\providecommand{\websiteicon}{%
  \raisebox{-1.5pt}{\includegraphics[height=1.2em]{logo/ms-logo.png}}%
}
\providecommand{\huggingfaceicon}{%
  \raisebox{-1.5pt}{\includegraphics[height=1.2em]{logo/hf-logo.pdf}}%
}
\providecommand{\foundryicon}{%
  \raisebox{-1.5pt}{\includegraphics[height=1.2em]{logo/foundry-logo.pdf}}%
}
\providecommand{\githubicon}{%
  \raisebox{-1.5pt}{\includegraphics[height=1.2em]{logo/github-logo.pdf}}%
}

\newcommand{\AIFRenderLinksContent}{%
  \begin{center}
    \small
    \begin{tabular}{@{}ll@{}}
      \ifdefempty{\weblink}{}{\websiteicon\ \href{\weblink}{\weblink}}%
      &
      \ifdefempty{\hflink}{}{\githubicon\ \href{\hflink}{\hflink}}%
      \\
      \ifdefempty{\foundrylink}{}{\huggingfaceicon\ \href{\foundrylink}{\foundrylink}}%
      &
      \ifdefempty{\ghlink}{}{\foundryicon\ \href{\ghlink}{\ghlink}}%
    \end{tabular}
  \end{center}
}

\newcommand{\AIFRenderLinks}{%
  \ifboolexpr{
    test {\ifdefempty{\weblink}}
    and test {\ifdefempty{\hflink}}
    and test {\ifdefempty{\foundrylink}}
    and test {\ifdefempty{\ghlink}}
  }{}{\AIFRenderLinksContent}%
}

% ---------------------------------------------------------------------------
% Custom \maketitle (no page break)
% ---------------------------------------------------------------------------
\renewcommand{\maketitle}{%
  \thispagestyle{firstpage}%
  \begingroup
  \setlength{\parindent}{0pt}%
  \setlength{\parskip}{6pt}%
  \vspace*{\AIFTitleTopGap}%
  \begin{center}
    {\LARGE\bfseries \@title\par}%
    \vspace{\AIFTitleAuthorGap}%
    {\@author\par}%
    {\footnotesize \@thanks\par}%
  \end{center}
  \AIFRenderLinks
  \ifx\abstracttext\@empty
  \else
    \begin{tcolorbox}[
        colback=aifrontiersabstractpurple!\AIFAbstractBackgroundStrength!white,
        colframe=aifrontiersabstractpurple!\AIFAbstractFrameStrength!white,
        boxrule=\AIFAbstractBoxRule,
        enhanced,
        arc=\AIFAbstractArc,
        before skip=\AIFAbstractTopGap,
        after skip=\AIFAbstractBottomGap,
        left=\AIFAbstractSidePadding,
        right=\AIFAbstractSidePadding,
        top=\AIFAbstractVerticalPadding,
        bottom=\AIFAbstractVerticalPadding
      ]
      {\centering\AIFAbstractTitleSize\bfseries\color{black}Abstract\par}
      \vspace{\AIFAbstractTitleGap}
      \abstracttext
    \end{tcolorbox}
  \fi
  \endgroup
}

% ---------------------------------------------------------------------------
% Section headings
% ---------------------------------------------------------------------------
\RequirePackage{titlesec}
\titleformat{\section}
  {\normalfont\Large\bfseries}
  {\thesection}{0.75em}{}
\titleformat{\subsection}
  {\normalfont\large\bfseries}
  {\thesubsection}{0.75em}{}
\titleformat{\subsubsection}
  {\normalfont\normalsize\bfseries}
  {\thesubsubsection}{0.75em}{}

% ---------------------------------------------------------------------------
% Convenience macros
% ---------------------------------------------------------------------------
\newcommand{\email}[1]{\href{mailto:#1}{\texttt{#1}}}
\newcommand{\affiliation}[1]{%
  {\normalsize\textit{#1}\par}
}

\endinput
