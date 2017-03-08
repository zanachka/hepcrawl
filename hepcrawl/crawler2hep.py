# -*- coding: utf-8 -*-
#
# This file is part of hepcrawl.
# Copyright (C) 2015, 2016, 2017 CERN.
#
# hepcrawl is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Convert a crawler record to a valid HEP record.

Don't forget to add pipelines to the ITEM_PIPELINES setting
See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
"""

from inspire_schemas.api import LiteratureBuilder


def crawler2hep(crawler_record):

    def _filter_affiliation(affiliations):
        return [
            affilation.get('value')
            for affilation in affiliations
            if affilation.get('value')
        ]

    builder = LiteratureBuilder('hepcrawl')

    for author in crawler_record.get('authors', []):
        builder.add_author(builder.make_author(
            author['full_name'],
            affiliations=_filter_affiliation(author['affiliations']),
        ))

    for title in crawler_record.get('titles', []):
        builder.add_title(
            title=title.get('title'),
            source=title.get('source')
        )

    for abstract in crawler_record.get('abstracts', []):
        builder.add_abstract(
            abstract=abstract.get('abstract'),
            source=abstract.get('source')
        )

    for arxiv_eprint in crawler_record.get('arxiv_eprint', []):
        builder.add_arxiv_eprint(
            arxiv_id=arxiv_eprint.get('value'),
            arxiv_categories=arxiv_eprint.get('categories')
        )

    for doi in crawler_record.get('dois', []):
        builder.add_doi(
            doi=doi.get('value')
        )

    for public_note in crawler_record.get('public_notes', []):
        builder.add_public_note(
            public_note=public_note.get('value'),
            source=public_note.get('source')
        )

    for license in crawler_record.get('license', []):
        builder.add_license(
            url=license.get('url'),
            license=license.get('license')
        )

    for collaboration in crawler_record.get('collaborations', []):
        builder.add_collaboration(
            collaboration=collaboration.get('value')
        )

    for imprint in crawler_record.get('imprints', []):
        builder.add_imprint_date(
            imprint_date=imprint.get('date')
        )

    for copyright in crawler_record.get('copyright', []):
        builder.add_copyright(
            holder=copyright.get('holder'),
            material=copyright.get('material'),
            statement=copyright.get('statement')
        )

    builder.add_preprint_date(
        preprint_date=crawler_record.get('preprint_date')
    )

    builder.add_acquisition_source(
        method='hepcrawl',
        date=crawler_record.get('date'),
        source=crawler_record.get('source'),
        submission_number=crawler_record.get('submission_number')
    )

    try:
        builder.add_number_of_pages(
            number_of_pages=int(crawler_record.get('page_nr'))
        )
    except (TypeError, ValueError):
        pass

    publication_types = [
        'introductory',
        'lectures',
        'review',
    ]

    special_collections = [
        'cdf-internal-note',
        'cdf-note',
        'cds',
        'd0-internal-note',
        'd0-preliminary-note',
        'h1-internal-note',
        'h1-preliminary-note',
        'halhidden',
        'hephidden',
        'hermes-internal-note',
        'larsoft-internal-note',
        'larsoft-note',
        'zeus-internal-note',
        'zeus-preliminary-note',
    ]

    document_types = [
        'book',
        'note',
        'report',
        'proceedings',
        'thesis',
    ]

    added_doc_type = False

    for collection in crawler_record.get('collections', []):
        collection = collection['primary'].strip().lower()

        if collection == 'arxiv':
            continue  # ignored
        elif collection == 'citeable':
            builder.set_citeable(True)
        elif collection == 'core':
            builder.set_core(True)
        elif collection == 'noncore':
            builder.set_core(False)
        elif collection == 'published':
            builder.set_refereed(True)
        elif collection == 'withdrawn':
            builder.set_withdrawn(True)
        elif collection in publication_types:
            builder.add_publication_type(collection)
        elif collection in special_collections:
            builder.add_special_collection(collection.upper())
        elif collection == 'bookchapter':
            added_doc_type = True
            builder.add_document_type('book chapter')
        elif collection == 'conferencepaper':
            added_doc_type = True
            builder.add_document_type('conference paper')
        elif collection in document_types:
            added_doc_type = True
            builder.add_document_type(collection)

    if not added_doc_type:
        builder.add_document_type('article')

    builder.validate_record()

    return builder.record
