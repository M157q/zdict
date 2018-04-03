import json

from zdict.dictionary import DictBase
from zdict.exceptions import NotFoundError, QueryError
from zdict.models import Record


# The request limit per minute is 60
# The monthly limit is 3,000 requests
API_ID = 'YOUR_API_ID'
API_KEY = 'YOUR_API_KEY'


class OxfordDictionary(DictBase):
    """
    Docs:

    * https://developer.oxforddictionaries.com/documentation/
    """

    API = 'https://od-api.oxforddictionaries.com/api/v1/entries/en/{word}'

    @property
    def provider(self):
        return 'oxford'

    @property
    def title(self):
        return 'Oxford Dictionary'

    def _get_url(self, word) -> str:
        return self.API.format(word=word.lower())

    def show(self, record: Record):
        content = json.loads(record.content)

        # word
        self.color.print(record.word, 'lyellow')

        # results
        for headword in content['results']:
            for lex_ent in headword['lexicalEntries']:
                # lexical category
                print()
                self.color.print(lex_ent['lexicalCategory'], 'lred', end='')

                # pronunciation
                if 'pronunciations' in lex_ent:
                    pronunciations = [
                        '/' + pronun['phoneticSpelling'] + '/'
                        for pronun in lex_ent['pronunciations']
                    ]
                    pronunciations_str = '  '.join(pronunciations)
                    self.color.print('  ' + pronunciations_str)
                else:
                    print()

                # entry
                idx = 1
                for entry in lex_ent['entries']:
                    for sense in entry['senses']:
                        line_prefix = '{idx}.'.format(idx=idx)
                        self._show_sense(sense, line_prefix)
                        idx += 1

        print()

    def _show_sense(self, sense: dict, prefix='', indent=1):
        print()
        self.color.print(prefix, end=' ', indent=indent)

        # regions
        if 'regions' in sense:
            regions_str = ', '.join(sense['regions'])
            regions_str = '(' + regions_str + ')'
            self.color.print(regions_str, 'yellow', end=' ')

        # register
        if 'registers' in sense:
            registers_str = ', '.join(sense['registers'])
            self.color.print(registers_str, 'red', end=' ')

        # domain
        if 'domains' in sense:
            domains_str = ', '.join(sense['domains'])
            domains_str = '(' + domains_str + ') '
            self.color.print(domains_str, 'green', end='')

        # notes
        if 'notes' in sense:
            notes = [note['text'] for note in sense['notes']]
            notes_str = ', '.join(notes)
            notes_str = '[' + notes_str + '] '
            self.color.print(notes_str, 'magenta', end='')

        # definition
        if 'definitions' in sense:
            definition_str = '. '.join(sense['definitions'])
            print(definition_str)

        # cross ref
        if 'crossReferenceMarkers' in sense:
            xref_marker_str = '. '.join(sense['crossReferenceMarkers'])
            print(xref_marker_str)

        # example
        for example in sense.get('examples', []):
            print()
            print(' ' * (indent + 1), end='  ')
            self.color.print(example['text'], 'indigo', indent=indent+2)

        # subsenses
        if 'subsenses' in sense:
            for idx, subsense in enumerate(sense['subsenses'], 1):
                line_prefix = '{prefix}{idx}.'.format(prefix=prefix, idx=idx)
                self._show_sense(subsense, line_prefix, indent=indent + 1)

    def query(self, word: str):
        try:
            content = self._get_raw(word, headers={
                'app_id': API_ID,
                'app_key': API_KEY
            })
        except QueryError as exception:
            raise NotFoundError(exception.word)

        record = Record(
            word=word,
            content=content,
            source=self.provider,
        )
        return record
