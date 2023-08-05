"""Auto-generated file, do not edit by hand. LU metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_LU = PhoneMetadata(id='LU', country_code=352, international_prefix='00',
    general_desc=PhoneNumberDesc(national_number_pattern='[24-9]\\d{3,10}|3(?:[0-46-9]\\d{2,9}|5[013-9]\\d{1,8})', possible_number_pattern='\\d{4,11}'),
    fixed_line=PhoneNumberDesc(national_number_pattern='(?:2(?:2\\d{1,2}|3[2-9]|[67]\\d|4[1-8]\\d?|5[1-5]\\d?|9[0-24-9]\\d?)|3(?:[059][05-9]|[13]\\d|[26][015-9]|4[0-26-9]|7[0-389]|8[08])\\d?|4\\d{2,3}|5(?:[01458]\\d|[27][0-69]|3[0-3]|[69][0-7])\\d?|7(?:1[019]|2[05-9]|3[05]|[45][07-9]|[679][089]|8[06-9])\\d?|8(?:0[2-9]|1[0-36-9]|3[3-9]|[469]9|[58][7-9]|7[89])\\d?|9(?:0[89]|2[0-49]|37|49|5[0-27-9]|7[7-9]|9[0-478])\\d?)\\d{1,7}', possible_number_pattern='\\d{4,11}', example_number='27123456'),
    mobile=PhoneNumberDesc(national_number_pattern='6[269][18]\\d{6}', possible_number_pattern='\\d{9}', example_number='628123456'),
    toll_free=PhoneNumberDesc(national_number_pattern='800\\d{5}', possible_number_pattern='\\d{8}', example_number='80012345'),
    premium_rate=PhoneNumberDesc(national_number_pattern='90[01]\\d{5}', possible_number_pattern='\\d{8}', example_number='90012345'),
    shared_cost=PhoneNumberDesc(national_number_pattern='801\\d{5}', possible_number_pattern='\\d{8}', example_number='80112345'),
    personal_number=PhoneNumberDesc(national_number_pattern='70\\d{6}', possible_number_pattern='\\d{8}', example_number='70123456'),
    voip=PhoneNumberDesc(national_number_pattern='20\\d{2,8}', possible_number_pattern='\\d{4,10}', example_number='2012345'),
    pager=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    uan=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    emergency=PhoneNumberDesc(national_number_pattern='11[23]', possible_number_pattern='\\d{3}', example_number='112'),
    voicemail=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    no_international_dialling=PhoneNumberDesc(national_number_pattern='NA', possible_number_pattern='NA'),
    national_prefix_for_parsing='(15(?:0[06]|1[12]|35|4[04]|55|6[26]|77|88|99)\\d)',
    number_format=[NumberFormat(pattern='(\\d{2})(\\d{3})', format=u'\\1 \\2', leading_digits_pattern=['[2-5]|7[1-9]|[89](?:[1-9]|0[2-9])'], domestic_carrier_code_formatting_rule=u'$CC \\1'),
        NumberFormat(pattern='(\\d{2})(\\d{2})(\\d{2})', format=u'\\1 \\2 \\3', leading_digits_pattern=['[2-5]|7[1-9]|[89](?:[1-9]|0[2-9])'], domestic_carrier_code_formatting_rule=u'$CC \\1'),
        NumberFormat(pattern='(\\d{2})(\\d{2})(\\d{3})', format=u'\\1 \\2 \\3', leading_digits_pattern=['20'], domestic_carrier_code_formatting_rule=u'$CC \\1'),
        NumberFormat(pattern='(\\d{2})(\\d{2})(\\d{2})(\\d{1,2})', format=u'\\1 \\2 \\3 \\4', leading_digits_pattern=['2(?:[0367]|4[3-8])'], domestic_carrier_code_formatting_rule=u'$CC \\1'),
        NumberFormat(pattern='(\\d{2})(\\d{2})(\\d{2})(\\d{3})', format=u'\\1 \\2 \\3 \\4', leading_digits_pattern=['20'], domestic_carrier_code_formatting_rule=u'$CC \\1'),
        NumberFormat(pattern='(\\d{2})(\\d{2})(\\d{2})(\\d{2})(\\d{1,2})', format=u'\\1 \\2 \\3 \\4 \\5', leading_digits_pattern=['2(?:[0367]|4[3-8])'], domestic_carrier_code_formatting_rule=u'$CC \\1'),
        NumberFormat(pattern='(\\d{2})(\\d{2})(\\d{2})(\\d{1,4})', format=u'\\1 \\2 \\3 \\4', leading_digits_pattern=['2(?:[12589]|4[12])|[3-5]|7[1-9]|[89](?:[1-9]|0[2-9])'], domestic_carrier_code_formatting_rule=u'$CC \\1'),
        NumberFormat(pattern='(\\d{3})(\\d{2})(\\d{3})', format=u'\\1 \\2 \\3', leading_digits_pattern=['[89]0[01]|70'], domestic_carrier_code_formatting_rule=u'$CC \\1'),
        NumberFormat(pattern='(\\d{3})(\\d{3})(\\d{3})', format=u'\\1 \\2 \\3', leading_digits_pattern=['6'], domestic_carrier_code_formatting_rule=u'$CC \\1')])
