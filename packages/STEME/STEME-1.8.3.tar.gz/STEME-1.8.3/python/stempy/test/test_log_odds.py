#
# Copyright John Reid 2011
#

"""
Test STEME makes correct log odds matrices.
"""

from setup_environment import init_test_env, update_path_for_stempy, logging
init_test_env(__file__, level=logging.INFO)
update_path_for_stempy()

import stempy, numpy
from itertools import imap

def distance(a, b):
    return numpy.sqrt(((a-b)**2).sum())

def rmse(a, b):
    return numpy.sqrt(((a-b)**2/a.size).sum())


# inputs
back = numpy.array([0.23644793, 0.26355207000000003, 0.26355207000000003, 0.23644793])
log_odds_range = 100
theta = numpy.array(
    [
        [0.00029519092384519346, 0.00032902880149812734, 0.99908058935081134   , 0.00029519092384519346],
        [0.00029519092384519346, 0.00032902880149812734, 0.99908058935081134   , 0.00029519092384519346],
        [0.99904675147315847   , 0.00032902880149812734, 0.00032902880149812734, 0.00029519092384519346],
        [0.00029519092384519346, 0.00032902880149812734, 0.99908058935081134   , 0.00029519092384519346],
        [0.12513913599250936   , 0.0003290288014981274 , 0.87423664428214731   , 0.00029519092384519351],
        [0.99904675147315847   , 0.00032902880149812734, 0.00032902880149812734, 0.00029519092384519346],
    ]
)

# target values
target_log_odds = numpy.array(
    [
        [-9.6456584324087107, -9.6456584324087107, 1.9225130321842525, 
  -9.6456584324087107, -6.596842896800303],
        [-9.6456584324087107, -9.6456584324087107, 1.9225130321842525, 
  -9.6456584324087107, -6.596842896800303],
        [2.0790296803960482, -9.6456584324087107, -9.6456584324087107, 
  -9.6456584324087107, -6.8733801982404188],
        [-9.6456584324087107, -9.6456584324087107, 1.9225130321842525, 
  -9.6456584324087107, -6.596842896800303],
        [-0.91798946339893628, -9.6456584324087107, 1.729935827653132, 
  -9.6456584324087107, -4.5839577562416984],
        [2.0790296803960482, -9.6456584324087107, -9.6456584324087107, 
  -9.6456584324087107, -6.8733801982404188],
    ]
)
target_scaled_log_odds = numpy.array(
    [
        [0, 0, 99, 0, 26],
        [0, 0, 99, 0, 26],
        [100, 0, 0, 0, 24],
        [0, 0, 99, 0, 26],
        [74, 0, 97, 0, 43],
        [100, 0, 0, 0, 24],
    ]
)
target_pdf = numpy.array(
    [
        0.11635637013708799, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0.054920206704705536, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.061436163432382465, 0, 0.12520957221273601, 
        0.071885087309824, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0.059098918084411395, 0.033929761210236928, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.06611065412832462, 
        0.037955326099587072, 0.044912129163264009, 0.077354604822527998, 
        0.011102670553087998, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0.021198524965060615, 0.036511373476233219, 0.0052404605010575346, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0.023713604198203397, 0.040843231346294785, 0.011232138538942466, 
        0.027746760425472007, 0.011947438964736001, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0025346062458224644, 
        0.013096470920822787, 0.0056391911913553916, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0028353222410895367, 0.014650289504649219, 
        0.0063082477733806082, 0.0033175474421760004, 0.0042854944112640002, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0.0015658823927070724, 0.0020227533621166079, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0017516650494689284, 
        0.0022627410491473923, 0, 0.00051239607091200005, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.00024185094547046402, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0.00027054512544153608, 0, 0, 0, 0, 0, 0
    ]
)
target_pdf_1 = numpy.array(
    [
        0.73599999999999999, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0.26400000000000001, 0
    ]
)
target_pdf_2 = numpy.array(
    [
        0.54169599999999996, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0.38860800000000006, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.069696000000000008, 0, 0
    ]
)
target_pdf_3 = numpy.array(
    [
        0.41385574399999997, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0.29689651200000006, 0.12784025599999999, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.053247744000000007, 
        0.091711488000000008, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0.016448256000000001, 0, 0
    ]
)
target_pdf_4 = numpy.array(
    [
        0.304597827584, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0.32777374924800001, 0.094090428415999988, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.11757101875200003, 
        0.10124948275200001, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0.014057404416000003, 0.036317749248000006, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0043423395840000009, 
        0, 0, 0
    ]
)
target_pdf_5 = numpy.array(
    [
        0.152298913792, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0.071885087309824, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0.080413826482176001, 0, 0.16388687462400001, 
        0.047045214207999994, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0.077354604822527998, 0.022205341106175995, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.086532269801472009, 
        0.024839873101823999, 0.058785509376000016, 0.050624741376000003, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0.027746760425472007, 0.023894877929472001, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.031038748950528008, 
        0.026729863446528002, 0.0070287022080000013, 0.018158874624000003, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0.0033175474421760004, 0.0085709888225280004, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0037111547658240009, 
        0.0095878858014720025, 0, 0.0021711697920000004, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0010247921418240001, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
        0.0011463776501760004, 0, 0, 0, 0, 0, 0
      ]
)
target_cdf = numpy.array(
    [
        1, 0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.88364362986291201, 
        0.88364362986291201, 0.88364362986291201, 0.82872342315820646, 
        0.82872342315820646, 0.82872342315820646, 0.82872342315820646, 
        0.82872342315820646, 0.82872342315820646, 0.82872342315820646, 
        0.82872342315820646, 0.82872342315820646, 0.82872342315820646, 
        0.82872342315820646, 0.82872342315820646, 0.82872342315820646, 
        0.82872342315820646, 0.82872342315820646, 0.82872342315820646, 
        0.82872342315820646, 0.82872342315820646, 0.82872342315820646, 
        0.82872342315820646, 0.82872342315820646, 0.82872342315820646, 
        0.82872342315820646, 0.76728725972582401, 0.76728725972582401, 
        0.64207768751308802, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.57019260020326401, 
        0.57019260020326401, 0.57019260020326401, 0.51109368211885264, 
        0.4771639209086157, 0.4771639209086157, 0.4771639209086157, 
        0.4771639209086157, 0.4771639209086157, 0.4771639209086157, 
        0.4771639209086157, 0.4771639209086157, 0.4771639209086157, 
        0.4771639209086157, 0.4771639209086157, 0.4771639209086157, 
        0.4771639209086157, 0.4771639209086157, 0.4771639209086157, 
        0.4771639209086157, 0.4771639209086157, 0.4771639209086157, 
        0.4771639209086157, 0.4771639209086157, 0.4771639209086157, 
        0.4771639209086157, 0.41105326678029108, 0.37309794068070401, 
        0.32818581151743997, 0.25083120669491199, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.23972853614182402, 
        0.23972853614182402, 0.23972853614182402, 0.21853001117676341, 
        0.1820186377005302, 0.17677817719947267, 0.17677817719947267, 
        0.17677817719947267, 0.17677817719947267, 0.17677817719947267, 
        0.17677817719947267, 0.17677817719947267, 0.17677817719947267, 
        0.17677817719947267, 0.17677817719947267, 0.17677817719947267, 
        0.17677817719947267, 0.17677817719947267, 0.17677817719947267, 
        0.17677817719947267, 0.17677817719947267, 0.17677817719947267, 
        0.17677817719947267, 0.17677817719947267, 0.17677817719947267, 
        0.17677817719947267, 0.15306457300126927, 0.11222134165497448, 
        0.10098920311603202, 0.073242442690560003, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.061295003725824006, 
        0.061295003725824006, 0.061295003725824006, 0.058760397480001544, 
        0.045663926559178759, 0.040024735367823368, 0.040024735367823368, 
        0.040024735367823368, 0.040024735367823368, 0.040024735367823368, 
        0.040024735367823368, 0.040024735367823368, 0.040024735367823368, 
        0.040024735367823368, 0.040024735367823368, 0.040024735367823368, 
        0.040024735367823368, 0.040024735367823368, 0.040024735367823368, 
        0.040024735367823368, 0.040024735367823368, 0.040024735367823368, 
        0.040024735367823368, 0.040024735367823368, 0.040024735367823368, 
        0.040024735367823368, 0.037189413126733829, 0.022539123622084611, 
        0.016230875848704002, 0.012913328406528, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0086278339952640011, 0.0086278339952640011, 0.0086278339952640011, 
        0.0070619516025569283, 0.0050391982404403204, 0.0050391982404403204, 
        0.0050391982404403204, 0.0050391982404403204, 0.0050391982404403204, 
        0.0050391982404403204, 0.0050391982404403204, 0.0050391982404403204, 
        0.0050391982404403204, 0.0050391982404403204, 0.0050391982404403204, 
        0.0050391982404403204, 0.0050391982404403204, 0.0050391982404403204, 
        0.0050391982404403204, 0.0050391982404403204, 0.0050391982404403204, 
        0.0050391982404403204, 0.0050391982404403204, 0.0050391982404403204, 
        0.0050391982404403204, 0.0050391982404403204, 0.0032875331909713924, 
        0.0010247921418240001, 0.0010247921418240001, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00051239607091200005, 0.00051239607091200005, 
        0.00051239607091200005, 0.00027054512544153608, 0.00027054512544153608, 
        0.00027054512544153608, 0.00027054512544153608, 0.00027054512544153608, 
        0.00027054512544153608, 0.00027054512544153608, 0.00027054512544153608, 
        0.00027054512544153608, 0.00027054512544153608, 0.00027054512544153608, 
        0.00027054512544153608, 0.00027054512544153608, 0.00027054512544153608, 
        0.00027054512544153608, 0.00027054512544153608, 0.00027054512544153608, 
        0.00027054512544153608, 0.00027054512544153608, 0.00027054512544153608, 
        0.00027054512544153608, 0.00027054512544153608, 0.00027054512544153608, 0, 
        0, 0, 0, 0, 0
    ]
)
seq = 'GGAGGA'
target_score = 594
target_pvalue = 0.00027054512544153608

# make and check matrices
log_odds = stempy.make_log_odds(pssm=theta, background=back)
assert distance(log_odds, target_log_odds) < 1e-12

scaled_log_odds = stempy.scale_log_odds(log_odds, range_=log_odds_range)
assert (scaled_log_odds == target_scaled_log_odds).all()

# round background so results same as MEME (and MAST)
rounded_back = back.round(3)

pssm_pdf_1 = stempy.calc_pssm_pdf(scaled_log_odds[:1], range_=log_odds_range, background=rounded_back)
assert distance(pssm_pdf_1, target_pdf_1) < 1e-16

pssm_pdf = stempy.calc_pssm_pdf(scaled_log_odds, range_=log_odds_range, background=rounded_back)
assert distance(pssm_pdf, target_pdf) < 1e-16

pssm_cdf = stempy.calc_pssm_cdf(scaled_log_odds, range_=log_odds_range, background=rounded_back)
assert distance(pssm_cdf, target_cdf) < 1e-16

score = stempy.score_pssm_on_seq(scaled_log_odds, imap(stempy.index_for_base, seq))
assert score == target_score

p_value = pssm_cdf[score]
assert abs(p_value - target_pvalue) < 1e-16
