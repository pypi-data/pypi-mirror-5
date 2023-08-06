#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import shutil
import os
from itertools import izip

import polib

from c3po.conf import settings
from c3po.converters.unicode import UnicodeWriter, UnicodeReader


def _get_all_po_filenames(locale_root, lang, po_files_path):
    """
    Get all po filenames from locale folder and return list of them.
    Assumes a dictionary structure <locale_root>/<lang>/<po_files_path>/<filename>.
    """
    all_files = os.listdir(os.path.join(locale_root, lang, po_files_path))
    return filter(lambda s: s.endswith('.po'), all_files)


def _get_new_csv_writers(trans_title, meta_title, trans_csv_path, meta_csv_path):
    """
    Prepare new csv writers, write title rows and return them.
    """
    trans_writer = UnicodeWriter(trans_csv_path)
    trans_writer.writerow(trans_title)

    meta_writer = UnicodeWriter(meta_csv_path)
    meta_writer.writerow(meta_title)

    return trans_writer, meta_writer


def _prepare_locale_dirs(languages, locale_root):
    """
    Prepare locale dirs for writing po files. Create new directories if they doesn't exist.
    """
    trans_languages = []
    for i, t in enumerate(languages):
        lang = t.split(':')[0]
        trans_languages.append(lang)
        lang_path = os.path.join(locale_root, lang)
        if not os.path.exists(lang_path):
            os.makedirs(lang_path)
    return trans_languages


def _prepare_polib_files(files_dict, filename, languages, locale_root, po_files_path, header):
    """
    Prepare polib file object for writing/reading from them. Create directories and write header if needed.
    For each language, ensure there's a translation file named "filename" in the correct place.
    Assumes (and creates) a dictionary structure <locale_root>/<lang>/<po_files_path>/<filename>.
    """
    files_dict[filename] = {}
    for lang in languages:
        file_path = os.path.join(locale_root, lang, po_files_path)
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        if header is not None:
            _write_header(os.path.join(file_path, filename), lang, header)

        files_dict[filename][lang] = polib.pofile(os.path.join(file_path, filename), encoding="UTF-8")


def _write_entries(po_files, languages, msgid, msgstrs, metadata, comment):
    """
    Write msgstr for every language with all needed metadata and comment.
    Metadata are parser from string into dict, so read them only from gdocs.
    """
    for i, lang in enumerate(languages):
        meta = ast.literal_eval(metadata)
        entry = polib.POEntry(**meta)
        entry.tcomment = comment
        entry.msgid = msgid
        entry.msgstr = unicode(msgstrs[i])
        po_files[lang].append(entry)
        po_files[lang].save()


def _write_header(po_path, lang, header):
    """
    Write header into po file for specific lang. Metadata are read from settings file.
    """
    po_file = open(po_path, 'w')
    po_file.write(header + '\n')
    po_file.write('msgid ""' +
                  '\nmsgstr ""' +
                  '\n"MIME-Version: ' + settings.METADATA['MIME-Version'] + r'\n"'
                  '\n"Content-Type: ' + settings.METADATA['Content-Type'] + r'\n"'
                  '\n"Content-Transfer-Encoding: ' + settings.METADATA['Content-Transfer-Encoding'] + r'\n"'
                  '\n"Language: ' + lang + r'\n"' + '\n')
    po_file.close()


def _write_new_messages(po_file_path, trans_writer, meta_writer, msgids, languages_num):
    """
    Write new msgids which appeared in po files with empty msgstrs values and metadata.
    Look for all new msgids which are diffed with msgids list provided as an argument.
    """
    po_filename = os.path.basename(po_file_path)
    po_file = polib.pofile(po_file_path)

    new_trans = 0
    for entry in po_file:
        if entry.msgid.rstrip() not in msgids:
            new_trans += 1
            trans = [entry.tcomment, entry.msgid, entry.msgstr]
            trans += [''] * languages_num

            meta = dict(entry.__dict__)
            meta.pop('msgid', None)
            meta.pop('msgstr', None)
            meta.pop('tcomment', None)

            trans_writer.writerow(trans)
            meta_writer.writerow([po_filename, str(meta)])

    return new_trans


def po_to_csv_merge(languages, locale_root, po_files_path,
                    local_trans_csv, local_meta_csv, gdocs_trans_csv, gdocs_meta_csv):
    """
    Converts po file to csv GDocs spreadsheet readable format. Merges them if some msgid aren't in the spreadsheet.
    :param languages: list of language codes
    :param locale_root: path to locale root folder containing directories with languages
    :param po_files_path: path from lang directory to po file
    :param local_trans_csv: path where local csv with translations will be created
    :param local_meta_csv: path where local csv with metadata will be created
    :param gdocs_trans_csv: path to gdoc csv with translations
    """
    msgids = []

    trans_reader = UnicodeReader(gdocs_trans_csv)
    meta_reader = UnicodeReader(gdocs_meta_csv)

    try:
        trans_title = trans_reader.next()
        meta_title = meta_reader.next()
    except StopIteration:
        trans_title = ['comment', 'msgid']
        trans_title += map(lambda s: s + ':msgstr', languages)
        meta_title = ['file', 'metadata']

    trans_writer, meta_writer = _get_new_csv_writers(trans_title, meta_title, local_trans_csv, local_meta_csv)

    for trans_row, meta_row in izip(trans_reader, meta_reader):
        msgids.append(trans_row[1].rstrip())
        trans_writer.writerow(trans_row)
        meta_writer.writerow(meta_row)

    trans_reader.close()
    meta_reader.close()

    po_files = _get_all_po_filenames(locale_root, languages[0], po_files_path)

    new_trans = False
    for po_filename in po_files:
        po_file_path = os.path.join(locale_root, languages[0], po_files_path, po_filename)
        ret = _write_new_messages(po_file_path, trans_writer, meta_writer, msgids, len(languages)-1)
        if ret > 0:
            new_trans = True

    trans_writer.close()
    meta_writer.close()

    return new_trans


def csv_to_po(trans_csv_path, meta_csv_path, locale_root, po_files_path, header=None):
    """
    Converts GDocs spreadsheet generated csv file into po file.
    :param trans_csv_path: path to temporary file with translations
    :param meta_csv_path: path to temporary file with meta information
    :param locale_root: path to locale root folder containing directories with languages
    :param po_files_path: path from lang directory to po file
    """
    shutil.rmtree(locale_root)

    # read title row and prepare descriptors for po files in each lang
    trans_reader = UnicodeReader(trans_csv_path)
    meta_reader = UnicodeReader(meta_csv_path)
    try:
        title_row = trans_reader.next()
    except StopIteration:
        # empty file
        return

    trans_languages = _prepare_locale_dirs(title_row[2:], locale_root)

    po_files = {}

    meta_reader.next()
    # go through every row in downloaded csv file
    for trans_row, meta_row in izip(trans_reader, meta_reader):
        filename = meta_row[0].rstrip()
        metadata = meta_row[1].rstrip()
        comment = trans_row[0].rstrip()
        msgid = trans_row[1].rstrip()

        if filename not in po_files:
            _prepare_polib_files(po_files, filename, trans_languages, locale_root, po_files_path, header)

        _write_entries(po_files[filename], trans_languages, msgid, trans_row[2:], metadata, comment)

    trans_reader.close()
    meta_reader.close()
