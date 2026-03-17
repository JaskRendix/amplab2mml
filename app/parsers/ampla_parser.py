from lxml import etree


def parse_ampla_xml(xml_bytes):
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.fromstring(xml_bytes, parser)
