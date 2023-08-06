__title__ = 'starbase.client.utils'
__version__ = '0.1'
__build__ = 0x000001
__author__ = 'Artur Barseghyan'
__all__ = ('build_json_data',)

import base64

# Importing OrderedDict with fallback to separate package for Python 2.6 support.
try:
    from collections import OrderedDict
except ImportError, e:
    from ordereddict import OrderedDict

def build_json_data(row, columns, timestamp=None, encode_content=False, with_row_declaration=True):
    """
    Builds JSON data for read-write purposes. Used in `starbase.client.Table._build_table_data`.

    :param str row:
    :param dict columns:
    :param timestamp: Not yet used.
    :param bool encode_content:
    :param bool with_row_declaration:
    :return dict:
    """
    # Encoding the key if necessary
    if encode_content:
        row = base64.b64encode(row)

    cell = []

    # Building table data dictionary.
    if columns:
        # Data structure #1
        if ':' in columns.keys()[0]:
            # Single column case
            if 1 == len(columns):
                key, value = columns.items()[0]

                if encode_content:
                    key = base64.b64encode(key)
                    value = base64.b64encode(str(value))

                cell_data = {
                    "column": key,
                    "$": value
                }
                if timestamp:
                    cell_data.update({'timestamp': timestamp})

                cell.append(cell_data)

            # Multi-column case
            else:
                for column in columns.items():
                    key, value = column

                    if encode_content:
                        key = base64.b64encode(key)
                        value = base64.b64encode(str(value))

                    cell_data = {
                        "column": key,
                        "$": value
                    }

                    if timestamp:
                        cell_data.update({'timestamp': timestamp})

                    cell.append(cell_data)

        # Data structure #2. Here we have multi-column cases only and you're advised to make profit of it.
        else:
            for column, data in columns.items():
                for key, value in data.items():
                    column_family = '%s:%s' % (column, key)

                    if encode_content:
                        column_family = base64.b64encode(column_family)
                        value = base64.b64encode(str(value))

                    cell_data = {
                        "column": column_family,
                        "$": value
                    }

                    if timestamp:
                        cell_data.update({'timestamp': timestamp})

                    cell.append(cell_data)

    table_data = OrderedDict([
        ("key", row),
        ("Cell", cell)
    ])

    if with_row_declaration:
        return {"Row" : [table_data]}
    else:
        return table_data

def build_xml_data(row, columns, timestamp=None, encode_content=False, with_row_declaration=True):
    """
    Builds XML data for read-write purposes. Used in `starbase.client.Table._build_table_data`.
    """
    # TODO: this is not ready yet!

    # Initial table data
    if encode_content:
        row = base64.encodestring(row)

    xml = """
      xml_data = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><CellSet>"
      xml_data << "<Row key='%(row)s rescue ''}'>"
      """ % {'row': row}

    xml += "</Row></CellSet>"

    return xml
