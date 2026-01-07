"""Updates publications and citation metrics in my CV."""

import json
import re
import urllib.parse

import requests

LIBRARY = "d7O0jq6KSTqnvppvvHjpjQ"  # The ADS library where I keep my papers
MENTORED_STUDENTS = ["Razo-López, N.~B.", "Rosselli-Calderon, A.", "Rohoza, V."]
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
        match = re.search("[A-Z]+:", self.title)
        if match is not None:
            tex_title = tex_title.replace(match.group(), rf"{match.group()[:-1]}\@:")

        # Inter-sentence spacing for acronyms followed by period
        match = re.search(r"[A-Z]+\.", self.title)
        if match is not None:
            tex_title = tex_title.replace(match.group(), rf"{match.group()[:-1]}\@.")

        # Correct quotation marks
        match = re.search(r'".*"', self.title)
        if match is not None:
            tex_title = tex_title.replace(match.group(), rf"``{match.group()[1:-1]}''")

        # En dash
        tex_title = tex_title.replace("–", "--")
        # Z in Zytkow
        tex_title = tex_title.replace("Ż", r"\.{Z}")

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
        return self.data["bibstem"][0]

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

        if len(self.authors) <= MAX_AUTHORS:
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
    def volume(self) -> int:
        """Journal volume."""
        return self.data["volume"]

    @property
    def issue(self) -> int:
        """Journal issue."""
        return self.data["issue"]

    @property
    def page(self) -> int:
        """Starting page."""
        return self.data["page"][0]

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
            entry += f"{self.short_journal}, {self.volume}, {self.page}"

        entry += r"}\\\textit{" + self.tex_title + "}"
        return entry


def main() -> None:
    """Updates publications and citation metrics in my CV."""

    # The ADS library of my papers
    library = requests.get(
        f"https://api.adsabs.harvard.edu/v1/biblib/libraries/{LIBRARY}",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=10,
    )
    bibcodes_dict = {"bibcodes": library.json()["documents"]}

    # The metrics for the library
    metrics = requests.post(
        "https://api.adsabs.harvard.edu/v1/metrics",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-type": "application/json",
        },
        data=json.dumps(bibcodes_dict),
        timeout=10,
    ).json()

    # Get information about the papers
    bibcodes = bibcodes_dict["bibcodes"]
    encoded_query = urllib.parse.urlencode(
        {
            "q": "*:*",
            "fl": "bibcode,title,author,bibstem,doi,issue,page,pub,title,volume,year",
            "rows": len(bibcodes),
            "sort": "date desc",
        }
    )

    payload = "bibcode\n" + "\n".join(bibcodes)

    results = requests.post(
        f"https://api.adsabs.harvard.edu/v1/search/bigquery?{encoded_query}",
        headers={"Authorization": f"Bearer {TOKEN}"},
        data=payload,
        timeout=10,
    ).json()

    papers = results["response"]["docs"]

    n_first_author = 0

    with open("papers.tex", "w", encoding="utf-8") as tex_file:
        for paper in papers:
            paper_obj = Paper(paper)
            if MY_NAME in paper_obj.authors[0]:
                n_first_author += 1
            if paper_obj.journal != "arXiv e-prints":
                tex_file.write(f"{paper_obj.tex_entry}\n\n")

    with open("preprints.tex", "w", encoding="utf-8") as tex_file:
        for paper in papers:
            paper_obj = Paper(paper)
            if paper_obj.journal == "arXiv e-prints":
                tex_file.write(f"{paper_obj.tex_entry}\n\n")

    # Metrics
    h_index = metrics["indicators"]["h"]
    citations = metrics["citation stats"]["number of citing papers"]

    # Write them to TeX file
    with open("metrics.tex", "w", encoding="utf-8") as tex_file:
        tex_file.write(
            f"{n_first_author} first-author, {citations} citations, h-index {h_index}"
        )


main()
