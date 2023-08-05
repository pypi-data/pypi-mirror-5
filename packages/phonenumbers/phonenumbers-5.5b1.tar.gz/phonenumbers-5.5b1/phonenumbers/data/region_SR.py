"""Auto-generated file, do not edit by hand. SR metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_SR = PhoneMetadata(id='SR', country_code=597, international_prefix='00',
    general_desc=PhoneNumberDesc(national_number_pattern='[2-8]\\d{5,6}', possible_number_pattern='\\d{6,7}'),
    fixed_line=PhoneNumberDesc(national_number_pattern='(?:2[1-3]|3[0-7]|4\\d|5[2-58]|68\\d)\\d{4}', possible_number_pattern='\\d{6,7}', example_number='211234'),
    mobile=PhoneNumberDesc(national_number_pattern='(?:7[1-57]|8[1-9])\\d{5}', possible_number_pattern='\\d{7}', example_number='7412345'),
    toll_free=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    premium_rate=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    shared_cost=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    personal_number=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    voip=PhoneNumberDesc(national_number_pattern='56\\d{4}', possible_number_pattern='\\d{6}', example_number='561234'),
    pager=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    uan=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    emergency=PhoneNumberDesc(national_number_pattern='115', possible_number_pattern='\\d{3}', example_number='115'),
    voicemail=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    no_international_dialling=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    number_format=[NumberFormat(pattern='(\\d{3})(\\d{3})', format=u'\\1-\\2', leading_digits_pattern=['[2-4]|5[2-58]']),
        NumberFormat(pattern='(\\d{2})(\\d{2})(\\d{2})', format=u'\\1-\\2-\\3', leading_digits_pattern=['56']),
        NumberFormat(pattern='(\\d{3})(\\d{4})', format=u'\\1-\\2', leading_digits_pattern=['[6-8]'])])
