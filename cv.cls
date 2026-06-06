\RequirePackage{microtype}
\RequirePackage[explicit]{titlesec}
\RequirePackage[pdfpagemode=UseNone]{hyperref}
\RequirePackage{unicode-math}
\RequirePackage{xstring}
\RequirePackage[left=1in,right=1in,top=1in,bottom=1in]{geometry}
\RequirePackage[itemsep=0em,topsep=0em,leftmargin=1.7em]{etaremune}
\RequirePackage{siunitx}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[12pt]{article}

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

% Journal names
\newcommand\aj{AJ}%        % Astronomical Journal
\newcommand\araa{ARA\&A}%  % Annual Review of Astron and Astrophys
\newcommand\apj{ApJ}%    % Astrophysical Journal
\newcommand\apjl{ApJL}     % Astrophysical Journal, Letters
\newcommand\apjs{ApJS}%    % Astrophysical Journal, Supplement
\newcommand\ao{ApOpt}%   % Applied Optics
\newcommand\apss{Ap\&SS}%  % Astrophysics and Space Science
\newcommand\aap{A\&A}%     % Astronomy and Astrophysics
\newcommand\aapr{A\&A~Rv}%  % Astronomy and Astrophysics Reviews
\newcommand\aaps{A\&AS}%    % Astronomy and Astrophysics, Supplement
\newcommand\azh{AZh}%       % Astronomicheskii Zhurnal
\newcommand\baas{BAAS}%     % Bulletin of the AAS
\newcommand\icarus{Icarus}% % Icarus
\newcommand\jaavso{JAAVSO}  % The Journal of the American Association of Variable Star Observers
\newcommand\jrasc{JRASC}%   % Journal of the RAS of Canada
\newcommand\memras{MmRAS}%  % Memoirs of the RAS
\newcommand\mnras{MNRAS}%   % Monthly Notices of the RAS
\newcommand\pra{PhRvA}% % Physical Review A: General Physics
\newcommand\prb{PhRvB}% % Physical Review B: Solid State
\newcommand\prc{PhRvC}% % Physical Review C
\newcommand\prd{PhRvD}% % Physical Review D
\newcommand\pre{PhRvE}% % Physical Review E
\newcommand\prl{PhRvL}% % Physical Review Letters
\newcommand\pasp{PASP}%     % Publications of the ASP
\newcommand\pasj{PASJ}%     % Publications of the ASJ
\newcommand\qjras{QJRAS}%   % Quarterly Journal of the RAS
\newcommand\skytel{S\&T}%   % Sky and Telescope
\newcommand\solphys{SoPh}% % Solar Physics
\newcommand\sovast{Soviet~Ast.}% % Soviet Astronomy
\newcommand\ssr{SSRv}% % Space Science Reviews
\newcommand\zap{ZA}%       % Zeitschrift fuer Astrophysik
\newcommand\nat{Nature}%  % Nature
\newcommand\iaucirc{IAUC}% % IAU Cirulars
\newcommand\aplett{Astrophys.~Lett.}%  % Astrophysics Letters
\newcommand\apspr{Astrophys.~Space~Phys.~Res.}% % Astrophysics Space Physics Research
\newcommand\bain{BAN}% % Bulletin Astronomical Institute of the Netherlands
\newcommand\fcp{FCPh}%   % Fundamental Cosmic Physics
\newcommand\gca{GeoCoA}% % Geochimica Cosmochimica Acta
\newcommand\grl{Geophys.~Res.~Lett.}%  % Geophysics Research Letters
\newcommand\jcp{JChPh}%     % Journal of Chemical Physics
\newcommand\jgr{J.~Geophys.~Res.}%     % Journal of Geophysics Research
\newcommand\jqsrt{JQSRT}%   % Journal of Quantitiative Spectroscopy and Radiative Trasfer
\newcommand\memsai{MmSAI}% % Mem. Societa Astronomica Italiana
\newcommand\nphysa{NuPhA}%     % Nuclear Physics A
\newcommand\physrep{PhR}%       % Physics Reports
\newcommand\physscr{PhyS}%        % Physica Scripta
\newcommand\planss{Planet.~Space~Sci.}%  % Planetary Space Science
\newcommand\procspie{Proc.~SPIE}%      % Proceedings of the SPIE

\newcommand\actaa{AcA}%  % Acta Astronomica
\newcommand\caa{ChA\&A}%  % Chinese Astronomy and Astrophysics
\newcommand\cjaa{ChJA\&A}%  % Chinese Journal of Astronomy and Astrophysics
\newcommand\jcap{JCAP}%  % Journal of Cosmology and Astroparticle Physics
\newcommand\na{NewA}%  % New Astronomy
\newcommand\nar{NewAR}%  % New Astronomy Review
\newcommand\pasa{PASA}%  % Publications of the Astron. Soc. of Australia
\newcommand\rmxaa{RMxAA}%  % Revista Mexicana de Astronomia y Astrofisica

%% added feb 9, 2016
\newcommand\maps{M\&PS}% Meteoritics and Planetary Science
\newcommand\aas{AAS Meeting Abstracts}% American Astronomical Society Meeting Abstracts
\newcommand\dps{AAS/DPS Meeting Abstracts}% American Astronomical Society/Division for Planetary Sciences Meeting Abstracts

\let\astap=\aap{}
\let\apjlett=\apjl{}
\let\apjsupp=\apjs{}
\let\applopt=\ao{}