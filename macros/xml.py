from YAMLMacros.lib.syntax import meta, expect, pop_on, stack, rule

def xml_attribute_prefix(prefix):
    before_attr_start = r'(?:\s+|^)'
    caps = {
        0: 'meta.namespace.{}'.format(prefix),
        1: 'entity.other.attribute-name.namespace.xml',
        2: 'entity.other.attribute-name.xml punctuation.separator.namespace.xml',
    }
    return [
        rule( match = before_attr_start + r'({})\b(:)?\s*$'.format(prefix), captures = caps),
        rule( match = before_attr_start + r'({})\b(:)?\s*(/?>)'.format(prefix), captures = dict(caps, **{ '3': 'punctuation.definition.tag.end.xml' }), pop = True ),
    ]
