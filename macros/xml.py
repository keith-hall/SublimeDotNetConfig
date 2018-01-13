from YAMLMacros.lib.syntax import meta, expect, pop_on, stack, rule

before_attr_start = r'(?:\s+|^)'

def get_caps(prefix):
    return {
        0: 'meta.namespace.{}'.format(prefix),
        1: 'entity.other.attribute-name.namespace.xml',
        2: 'entity.other.attribute-name.xml punctuation.separator.namespace.xml',
    }

def xml_attribute_prefix(prefix):
    caps = get_caps(prefix)
    return [
        rule(match = before_attr_start + r'({})\b(:)?\s*$'.format(prefix), captures = caps),
        rule(match = before_attr_start + r'({})\b(:)?\s*(/?>)'.format(prefix), captures = dict(caps, **{ '3': 'punctuation.definition.tag.end.xml' }), pop = True),
    ]

# def commented_seq_join(seq, join):
#     print(dir(seq))
#     print([item for item in seq])
#     if len(seq):
#         print(seq[0], dir(seq[0]))
#     return join.join([item for item in seq])

def regex_alternatives(regex):
    # return strings in alphabetical order with longest item first
    items = regex.split(r'|') # doesn't do any fancy escape checking
    items.sort()
    items.sort(key = len, reverse=True)
    return r'|'.join(items)

def xml_attribute_xpath(prefix, localname, xpath_functions, keywords):
    localname_lcase = localname.lower()
    cap_dict = dict(get_caps(prefix), **{
        '3': 'entity.other.attribute-name.localname.xml',
        '4': 'punctuation.separator.key-value.xml meta.xpath.{}.xdt'.format(localname_lcase),
    })
    return [
        rule(match = before_attr_start + r'({})\b(:)({})\s*(=)\s*(")'.format(prefix, localname), captures = dict(cap_dict, **{ '5': 'string.quoted.double.xml meta.xpath.{}.xdt punctuation.definition.string.begin.xml'.format(localname_lcase) }), push = [
            rule(meta_content_scope = 'string.quoted.double.xml meta.xpath.{}.xdt'.format(localname_lcase)),
            rule(match = r'(?=>)', pop = True),
            rule(match = r'"', scope = 'string.quoted.double.xml meta.xpath.{}.xdt punctuation.definition.string.end.xml'.format(localname_lcase), pop = True),
            rule(match = r'\b({})\b'.format(regex_alternatives(keywords)), scope = 'support.function.{}.xdt'.format(localname_lcase)),
            rule(match = r'\s*(?=\b(?:{})\b)'.format(regex_alternatives(xpath_functions)), embed = 'xpath', escape = r'(?=[">])'),
            rule(match = r'[^"\s>]+', scope = 'invalid.deprecated.unknown-{}.xdt'.format(localname_lcase)),
        ]),
        rule(match = before_attr_start + r'({})\b(:)({})\s*(=)\s*(/?>)'.format(prefix, localname), captures = dict(cap_dict, **{ '5': 'meta.xpath.{}.xdt punctuation.definition.tag.end.xml'.format(localname_lcase) }), pop = True),
        rule(match = before_attr_start + r'({})\b(:)({})\s*(=\s*)?'.format(prefix, localname), captures = cap_dict),
    ]
