"""Updates publications and citation metrics in my CV."""
import json
import re
import urllib.parse
import requests

LIBRARY = 'd7O0jq6KSTqnvppvvHjpjQ'  # The ADS library where I keep my papers
MENTORED_STUDENTS = ['Razo-López, N. B.']
MY_NAME = 'Yarza, R.'

# If the number of authors in the paper is larger than MAX_AUTHORS,
# truncate author list and add "et al."
MAX_AUTHORS = 4


with open("api.key", encoding='utf-8') as key:
    TOKEN = key.read()


class Paper:
    """A scientific paper, including arXiv submissions."""

    def __init__(self, data: dict):
        self.data = data

    @property
    def title(self) -> str:
        """Full paper title."""
        return self.data['title'][0]

    @property
    def tex_title(self) -> str:
        """TeX-friendly title."""
        tex_title = self.title
        match = re.search('[A-Z]+:', self.title)
        if match is not None:
            tex_title = self.title.replace(
                match.group(),
                rf"{match.group()[:-1]}\@:"
            )
        return tex_title

    @property
    def authors(self) -> list:
        """List of authors' last names and initials."""
        original_authors = self.data['author']
        authors = []
        for original_author in original_authors:
            names = original_author.split(',')
            last_name = names[0]
            if len(names) == 1:  # Usually happens with collaborations
                first_name_initials = ''
            else:
                first_names = names[1].strip()
                first_name_initials = ' '.join(
                    [f'{name[0]}.' for name in first_names.split(' ')]
                )
            authors += [f'{last_name}, {first_name_initials}']
        return authors

    @property
    def journal(self) -> str:
        """Full name of the journal"""
        return self.data['pub']

    @property
    def short_journal(self) -> str:
        """Abbreviated journal name (e.g., ApJ)."""
        return self.data['bibstem'][0]

    @property
    def bibcode(self) -> str:
        """ADS bibcode."""
        return self.data['bibcode']

    @property
    def year(self) -> int:
        """Publication year."""
        return self.data['year']

    # @property
    # def journal_color(self) -> str:
    #     """Color in which I want to highlight the journal in my CV."""
    #     return 'arxivcolor' if self.journal == 'arXiv e-prints' else None

    @property
    def author_string(self) -> str:
        """List of authors for the entry in the CV."""
        my_position = [
            idx for idx, author
            in enumerate(self.authors)
            if author == MY_NAME][0]

        temp_authors = self.authors.copy()

        for idx, author in enumerate(temp_authors):
            for student in MENTORED_STUDENTS:
                if student == author:
                    temp_authors[idx] = r'\underline{' + author + '}'

        if len(self.authors) == MAX_AUTHORS:
            temp_authors[-1] = fr'\& {self.authors[-1]}'

        if my_position > MAX_AUTHORS - 1:
            author_string = ', '.join(self.authors[:MAX_AUTHORS - 1]) +\
                r', et al., incl.\ \textbf{' + MY_NAME + '}'
        else:
            temp_authors[my_position] = rf'\textbf{{{MY_NAME}}}'
            author_string = ', '.join(temp_authors[:MAX_AUTHORS])
            if len(self.authors) > MAX_AUTHORS:
                author_string += ', et al.'
        return author_string

    @property
    def volume(self) -> int:
        """Journal volume."""
        return self.data['volume']

    @property
    def issue(self) -> int:
        """Journal issue."""
        return self.data['issue']

    @property
    def page(self) -> int:
        """Starting page."""
        return self.data['page'][0]

    @property
    def tex_entry(self) -> str:
        """CV entry for the paper."""

        entry = (
            fr"\item {self.author_string} {self.year}, "
            r'\href{https://ui.adsabs.harvard.edu/abs/' + self.bibcode + '}'
        )
        if self.journal == 'arXiv e-prints':
            entry += r'{\color{arxivcolor}{' + self.short_journal + '}}'
        else:
            entry += '{' f'{self.short_journal}, {self.volume}, {self.page}' '}'
            # entry +=fr'{{{self.short_journal}, {self.volume}, {self.issue}}}'
        entry += r'\\\textit{' + self.tex_title + '}'
        return entry


def main() -> None:
    """Updates publications and citation metrics in my CV."""

    # The ADS library of my papers
    library = requests.get(
        f"https://api.adsabs.harvard.edu/v1/biblib/libraries/{LIBRARY}",
        headers={'Authorization': f'Bearer {TOKEN}'},
        timeout=10
    )
    bibcodes_dict = {"bibcodes": library.json()['documents']}

    # The metrics for the library
    metrics = requests.post(
        "https://api.adsabs.harvard.edu/v1/metrics",
        headers={'Authorization': f'Bearer {TOKEN}',
                 "Content-type": "application/json"},
        data=json.dumps(bibcodes_dict),
        timeout=10
    ).json()

    # Get information about the papers
    bibcodes = bibcodes_dict['bibcodes']
    encoded_query = urllib.parse.urlencode(
        {"q": "*:*",
         "fl": "bibcode,title,author,bibstem,doi,issue,page,pub,title,volume,year",
         "rows": len(bibcodes),
         "sort": "date desc"
         }
    )

    payload = "bibcode\n" + '\n'.join(bibcodes)

    results = requests.post(
        f"https://api.adsabs.harvard.edu/v1/search/bigquery?{encoded_query}",
        headers={'Authorization': f'Bearer {TOKEN}'},
        data=payload,
        timeout=10
    ).json()

    papers = results['response']['docs']

    n_first_author = 0

    with open("papers.tex", "w", encoding='utf-8') as tex_file:
        for paper in papers:
            paper_obj = Paper(paper)
            if MY_NAME in paper_obj.authors[0]:
                n_first_author += 1
            tex_file.write(f'{paper_obj.tex_entry}\n\n')

    # Important metrics
    # h_index = metrics['indicators']['h']
    citations = metrics['citation stats']['number of citing papers']

    # Write them to the TeX file
    with open("metrics.tex", "w", encoding='utf-8') as tex_file:
        tex_file.write(
            f"{n_first_author} first-author"
            f", {citations} citations"
            # f", h-index {h_index}"
        )


main()
