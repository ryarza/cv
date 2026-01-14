"""Updates publications and citation metrics in my CV."""

import functools
import json
import re
import urllib.parse

import requests

LIBRARY = "d7O0jq6KSTqnvppvvHjpjQ"  # The ADS library where I keep my papers
LIBRARY_NONPAPERS = "GNkwlF-pQ0C0kCEat5Mc2g"  # Conference abstracts, code ,etc
MENTORED_STUDENTS = [
    "Razo-López, N.~B.",
    "Rosselli-Calderon, A.",
    "Rohoza, V.",
    "Kotten, B.",
]
MY_NAME = "Yarza, R."

# If the number of authors exceeds MAX_AUTHORS, list MAX_AUTHORS - 1 authors and add "et al."
# i.e., either five authors or four authors + et al.
MAX_AUTHORS = 5


with open("api.key", encoding="utf-8") as key:
    TOKEN = key.read()


class Paper:
    """A scientific paper, including arXiv submissions."""

    def __init__(self, data: dict):
        self.data = data

    @property
    def title(self) -> str:
        """Full paper title."""
        return self.data["title"][0]

    @property
    def tex_title(self) -> str:
        """TeX-friendly title."""
        tex_title = self.title

        # Inter-sentence spacing for acronyms followed by colon
        match = re.search("[A-Z]+:", tex_title)
        if match is not None:
            tex_title = tex_title.replace(match.group(), rf"{match.group()[:-1]}\@:")

        # Inter-sentence spacing for acronyms followed by period
        match = re.search(r"[A-Z]+\.", tex_title)
        if match is not None:
            tex_title = tex_title.replace(match.group(), rf"{match.group()[:-1]}\@.")

        # Correct quotation marks
        match = re.search(r'".*"', tex_title)
        if match is not None:
            tex_title = tex_title.replace(match.group(), rf"``{match.group()[1:-1]}''")

        # Money sign
        while True:
            match = re.search(r"\$.*?\$", tex_title)
            if match is not None:
                print(tex_title)
                print(match.group())
                tex_title = tex_title.replace(
                    match.group(), rf"\( {match.group()[1:-1]} \)"
                )
                print(tex_title)
            else:
                break

        # En dash
        tex_title = tex_title.replace("–", "--")
        # Z in Zytkow
        tex_title = tex_title.replace("Ż", r"\.{Z}")
        # Ampersand
        tex_title = tex_title.replace("&", r"\&")

        # Corrections for specific papers
        tex_title = tex_title.replace(
            r"\( 1.4 \) M\( _\odot \)", r"\( \qty{1.4}{\solarmass} \)"
        )

        return tex_title

    @property
    def authors(self) -> list:
        """List of authors' last names and initials."""
        original_authors = self.data["author"]
        authors = []
        for original_author in original_authors:
            names = original_author.split(",")
            last_name = names[0]
            if len(names) == 1:  # Usually happens with collaborations
                first_name_initials = ""
            else:
                first_names = names[1].strip()
                first_name_initials = " ".join(
                    [f"{first_name[0]}." for first_name in first_names.split(" ")]
                )
            authors += [f"{last_name}, {first_name_initials.replace('. ', '.~')}"]
        return authors

    @property
    def journal(self) -> str:
        """Full name of the journal"""
        return self.data["pub"]

    @property
    def short_journal(self) -> str:
        """Abbreviated journal name (e.g., ApJ)."""
        short_journal = self.data["bibstem"][0]
        short_journal = short_journal.replace("zndo", "Zenodo")
        return short_journal

    @property
    def bibcode(self) -> str:
        """ADS bibcode."""
        return self.data["bibcode"]

    @property
    def year(self) -> int:
        """Publication year."""
        return self.data["year"]

    # @property
    # def journal_color(self) -> str:
    #     """Color in which I want to highlight the journal in my CV."""
    #     return 'arxivcolor' if self.journal == 'arXiv e-prints' else None

    @property
    def author_string(self) -> str:
        """List of authors for the entry in the CV."""
        if len(self.authors) == 1:
            author_string = self.authors[0]
        elif 1 < len(self.authors) <= MAX_AUTHORS:
            # If we don't need to truncate, return all authors
            last_author = r", \& " f"{self.authors[-1]}"
            author_string = ", ".join(self.authors[:-1]) + last_author
        else:
            my_position = self.authors.index(MY_NAME)
            author_string_parts = self.authors[: MAX_AUTHORS - 1] + ["et al."]
            author_string = ", ".join(author_string_parts)
            if my_position > MAX_AUTHORS - 2:
                author_string += r"\ incl.\ Yarza, R."

        author_string = author_string.replace("Yarza, R.", r"\textbf{Yarza, R.}")

        for mentee in MENTORED_STUDENTS:
            if mentee in author_string:
                author_string = author_string.replace(
                    mentee, r"\underline{" f"{mentee}" r"}"
                )

        return author_string

    @property
    def volume(self) -> int | None:
        """Journal volume."""
        try:
            return self.data["volume"]
        except KeyError:
            return None

    @property
    def issue(self) -> int:
        """Journal issue."""
        return self.data["issue"]

    @property
    def page(self) -> int | None:
        """Starting page."""
        try:
            return self.data["page"][0]
        except KeyError:
            return None

    @property
    def tex_entry(self) -> str:
        """CV entry for the paper."""

        entry = (
            rf"\item {self.author_string} {self.year}, "
            r"\href{https://ui.adsabs.harvard.edu/abs/" + self.bibcode + "}{"
        )
        if self.journal == "arXiv e-prints":
            entry += f"{self.page}".replace(":", r":\allowbreak")
        else:
            entry += f"{self.short_journal}"
            if self.volume is not None:
                entry += f", {self.volume}"
            if self.page is not None:
                entry += f", {self.page}"

        entry += r"}\\\textit{" + self.tex_title + "}"
        return entry

    @property
    def doctype(self) -> str:
        """Document type (e.g., "article" or "eprint")"""
        return self.data["doctype"]


class Library:
    """An ADS library"""

    def __init__(self, library_id: str):
        self._library_id = library_id

    @property
    def library_id(self) -> str:
        """ID of the library"""
        return self._library_id

    @functools.cached_property
    def library_data(self):
        """Information about the library"""
        return requests.get(
            f"https://api.adsabs.harvard.edu/v1/biblib/libraries/{self.library_id}",
            headers={"Authorization": f"Bearer {TOKEN}"},
            timeout=10,
        )

    @property
    def _query(self):
        return urllib.parse.urlencode(
            {
                "q": "*:*",
                "fl": "bibcode,doctype,title,author,bibstem,doi,issue,page,pub,title,volume,year",
                "rows": len(self.bibcodes),
                "sort": "date desc",
            }
        )

    @property
    def bibcodes(self):
        """Bibcodes of entries in the library"""
        return self.bibcodes_dict["bibcodes"]

    @property
    def bibcodes_dict(self):
        """Same as bibcodes but as a dictionary"""
        return {"bibcodes": self.library_data.json()["documents"]}

    @functools.cached_property
    def metrics(self):
        """Aggregate metrics of the library"""
        return requests.post(
            "https://api.adsabs.harvard.edu/v1/metrics",
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Content-type": "application/json",
            },
            data=json.dumps(self.bibcodes_dict),
            timeout=10,
        ).json()

    @functools.cached_property
    def data(self):
        """Information for all papers in the library"""
        return requests.post(
            f"https://api.adsabs.harvard.edu/v1/search/bigquery?{self._query}",
            headers={"Authorization": f"Bearer {TOKEN}"},
            data="bibcode\n" + "\n".join(self.bibcodes),
            timeout=10,
        ).json()

    @property
    def entries(self):
        """Entries in the database"""
        return self.data["response"]["docs"]


def main() -> None:
    """Updates publications and citation metrics in my CV."""

    library = Library(LIBRARY)

    n_first_author = 0

    with open("data/papers.tex", "w", encoding="utf-8") as tex_file:
        for paper in library.entries:
            paper_obj = Paper(paper)
            if MY_NAME in paper_obj.authors[0]:
                n_first_author += 1
            if paper_obj.doctype == "article":
                print(paper_obj.data)
                tex_file.write(f"{paper_obj.tex_entry}\n\n")

    with open("data/preprints.tex", "w", encoding="utf-8") as tex_file:
        for paper in library.entries:
            paper_obj = Paper(paper)
            if paper_obj.doctype == "eprint":
                tex_file.write(f"{paper_obj.tex_entry}\n\n")

    # Metrics
    h_index = library.metrics["indicators"]["h"]
    citations = library.metrics["citation stats"]["number of citing papers"]

    # Write them to TeX file
    with open("data/metrics.tex", "w", encoding="utf-8") as tex_file:
        tex_file.write(
            f"{n_first_author} first-author, {citations} citations, h-index {h_index}"
        )

    ## Conferences, software, and others
    library = Library(LIBRARY_NONPAPERS)
    with open("data/nonpapers.tex", "w", encoding="utf-8") as tex_file:
        for paper in library.entries:
            paper_obj = Paper(paper)
            assert paper_obj.doctype != "article", "Article found in non-article list!"
            print(paper_obj.data)
            tex_file.write(f"{paper_obj.tex_entry}\n\n")


main()
