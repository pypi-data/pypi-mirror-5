# coding: utf-8

import re

from django.utils.translation import ugettext as _
from django.core.validators import RegexValidator

def validate_str(value):
	"""Validate any string value"""
	regexObj = re.compile('\w+', re.L)
	obj = RegexValidator(regexObj, _('Validation error. Text expected.'))
	obj.__call__(value)

def validate_txt_field(value):
	"""Validate a text field"""
	#regexObj = re.compile("^(\w*)\s?(\s?\w+)*$", re.L)
	regexObj = re.compile('\w+', re.L)
	obj = RegexValidator(regexObj, _('Validation error. Text field expected.'))
	obj.__call__(value)

def validate_domain(value):
	"""Validate domain."""
	regexObj = re.compile("^([a-z0-9]([-a-z0-9]*[a-z0-9])?\\.)+((a[cdefgilmnoqrstuwxz]|aero|arpa)|(b[abdefghijmnorstvwyz]|biz)|(c[acdfghiklmnorsuvxyz]|cat|com|coop)|d[ejkmoz]|(e[ceghrstu]|edu)|f[ijkmor]|(g[abdefghilmnpqrstuwy]|gov)|h[kmnrtu]|(i[delmnoqrst]|info|int)|(j[emop]|jobs)|k[eghimnprwyz]|l[abcikrstuvy]|(m[acdghklmnopqrstuvwxyz]|mil|mobi|museum)|(n[acefgilopruz]|name|net)|(om|org)|(p[aefghklmnrstwy]|pro)|qa|r[eouw]|s[abcdeghijklmnortvyz]|(t[cdfghjklmnoprtvwz]|travel)|u[agkmsyz]|v[aceginu]|w[fs]|y[etu]|z[amw])$", re.L)
	obj = RegexValidator(regexObj, _('Validation error. Internet domain expected.'))
	obj.__call__(value)

def validate_currency(value):
	"""Validate currency"""
	regexObj = re.compile('^[0-9]*\.?|\,?[0-9]{0,2}$')
	obj = RegexValidator(regexObj, _('Validation error. Currency expected.'))
	obj.__call__(value)

def validate_id(value):
	"""Validate Id"""
	regexObj = re.compile('^[1-9]+[0-9]*$')
	obj = RegexValidator(regexObj, _('Validation error. Id expected.'))
	obj.__call__(value)

def validate_user_id(value):
	"""Validate User Id"""
	#regexObj = re.compile('^[a-zA-Z0-9_.@-+]+')
	regexObj = re.compile('^[a-zA-Z0-9_]+')
	obj = RegexValidator(regexObj, _('Validation error. UserId expected.'))
	obj.__call__(value)

def validate_password(value):
	"""Validate Password"""
	regexObj = re.compile('^[a-zA-Z0-9_.$%&]+')
	obj = RegexValidator(regexObj, _('Validation error. Password expected.'))
	obj.__call__(value)

def validate_captcha(value):
	"""Validate Captcha"""
	regexObj = re.compile('^\w{6}$')
	obj = RegexValidator(regexObj, _('Validation error. Captcha text expected.'))
	obj.__call__(value)

def validate_email(value):
	"""Validate Email"""
	regexObj = re.compile('^([\w.])+\@([a-z0-9]([-a-z0-9]*[a-z0-9])?\\.)+((a[cdefgilmnoqrstuwxz]|aero|arpa)|(b[abdefghijmnorstvwyz]|biz)|(c[acdfghiklmnorsuvxyz]|cat|com|coop)|d[ejkmoz]|(e[ceghrstu]|edu)|f[ijkmor]|(g[abdefghilmnpqrstuwy]|gov)|h[kmnrtu]|(i[delmnoqrst]|info|int)|(j[emop]|jobs)|k[eghimnprwyz]|l[abcikrstuvy]|(m[acdghklmnopqrstuvwxyz]|mil|mobi|museum)|(n[acefgilopruz]|name|net)|(om|org)|(p[aefghklmnrstwy]|pro)|qa|r[eouw]|s[abcdeghijklmnortvyz]|(t[cdfghjklmnoprtvwz]|travel)|u[agkmsyz]|v[aceginu]|w[fs]|y[etu]|z[amw])')
	obj = RegexValidator(regexObj, _('Validation error. Email expected.'))
	obj.__call__(value)



"""validationMap = {
					Ch.FORMAT_TYPE_EMAIL: [validateEmail],
					Ch.FORMAT_TYPE_PASSWORD: [validatePassword],
					Ch.FORMAT_TYPE_USERID: [validateUserId],
					Ch.FORMAT_TYPE_CHAR: [validateTxtField]
				}"""
