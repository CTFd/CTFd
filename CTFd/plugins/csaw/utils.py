from marshmallow import ValidationError


CSAW_BRACKETS = [
    '',
    'High School',
    'Undergraduate',
    'Stacked',
    'Graduate',
    'Professional',
    'Other'
]

CSAW_REGIONS = [
    '',
    'CSAW Europe',
    'CSAW India',
    'CSAW MENA',
    'CSAW Mexico',
    'CSAW US-Canada',
]


def validate_csaw_region(region):
    if region.strip() == "":
        return
    if region not in CSAW_REGIONS:
        raise ValidationError("Invalid Region")


def validate_csaw_bracket(bracket):
    if bracket.strip() == "":
        return
    if bracket not in CSAW_BRACKETS:
        raise ValidationError("Invalid Bracket")
