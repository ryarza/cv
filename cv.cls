\ProvidesClass{cv}[CV]

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[12pt]{article}

\RequirePackage{microtype}
\RequirePackage[explicit]{titlesec}
\RequirePackage[pdfpagemode=UseNone]{hyperref}
\RequirePackage{unicode-math}
\RequirePackage[left=1in,right=1in,top=1in,bottom=1in]{geometry}
\RequirePackage[itemsep=0em,topsep=0em,leftmargin=1.7em]{etaremune}

\NewDocumentCommand\email{m}{\gdef\@email{#1}}
\NewDocumentCommand\website{m}{\gdef\@website{#1}}

\renewcommand{\maketitle}{
{\centering {\Large \@author}

\@email{} \(|\) \href{https://\@website}{\@website}

}
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{7.25pt plus 2.0pt}

\titleformat{name=\section,numberless}{\large\scshape}{}{0em}{#1}[\hrule]
% \titleformat{\section}{\large\scshape}{}{0em}{}[\hrule]
\titlespacing{\section}{0pt}{0em}{0pt}[0pt]

\renewcommand\labelitemi{\textendash{}}

\hypersetup{
pdftitle = {\@author's CV},
pdfauthor = {\@author}
}