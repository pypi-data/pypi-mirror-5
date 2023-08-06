# Valhalla
[![Build Status](https://travis-ci.org/petermelias/valhalla.png?branch=master)](https://travis-ci.org/petermelias/valhalla) [![Coverage Status](https://coveralls.io/repos/petermelias/valhalla/badge.png?branch=master)](https://coveralls.io/r/petermelias/valhalla?branch=master) [![Downloads](https://pypip.in/d/valhalla/badge.png)](https://crate.io/packages/valhalla) [![Downloads](https://pypip.in/v/valhalla/badge.png)](https://crate.io/packages/valhalla)

Very powerful and flexible data filtering / validation /sanitization library with a highly efficient API.
Declarative schema interface for defining filters, dict based definitions coming soon...

The API is designed to afford the programmer the least amount of typing for each
use case, with the option to be more verbose when necessary.

## Usage

```python

from valhalla import Schema

s = Schema('Signup Form', match=['password', 'password_confirm'])
s.email_address.email()
s.first_name.text()
s.last_name.text()
s.password.text()
s.password_confirm.text()
s.location.require(False)

```

Note: The field names are added dynamically, so long as you don't collide with any of the built-in ``` Schema ``` attributes. Calling the field name is not necessary, calling the filter functions is necessary however, as shown above.

The built-in ``` Schema ``` attributes are: [name, errors, valid, missing, add_field, required_fields, optional_fields, blank_fields, not_blank_fields, match_fields, validate, reset]

```python

test_data = {
    'email_address': 'petermelias@gmail.com',
    'first_name': 'Peter',
    'last_name': 'Elias',
    'password': '1234',
    'password_confirm': '12345'
}

s.validate(test_data)
assert_false(s.valid) # True
assert_false(s.password.valid) # True
print s.password.errors # This field must match [password_confirm]
assert_true(s.location.valid) # True, field is not required

print s.results # {'email_address': 'petermelias@gmail.com'} etc... only yields valid values.

# Field-wide options may specified at the Schema-level or at the Field-level, field-level takes precedence.
s = Schema(require=['some_field'])
s.some_field.require(False) # overrides the schema setting

# a more useful example...

s = Schema(require='all')
s.i_am_required
s.not_me_though.require(False)

# Field-wide options: [blank, require, match]
s = Schema(match=[('match_me', 'to_me'), ('and_me', 'to_other_me')], blank='all', required='all')
# these two must match
s.match_me 
s.to_me

# and these two must match
s.and_me
s.to_other_me

# May also be used declaratively
s = Schema()
s.i_am_required.require(True) # all fields are required by default though
s.i_can_be_blank.blank(True) # all fields CANNOT be blank by default
s.i_should_match.match('i_am_required')

'''
The difference between BLANK and REQUIRED is that a field must be included in the supplied DATA in order to be considered "present". If a value is not "present", and the field is required, an error is raised. If the value is "present", but BLANK (meaning some kind of empty value), and the field does NOT allow blanks, then an error is raised.

So, if a field is NOT REQUIRED, and NOT BLANK. Then you can omit the field entirely, but you cannot supply it with an empty value either.
'''
s.some_field.blank(False).require(False) # either supply me with a real value or go home. this is the default for all fields.

```
### Dict-Based Schema Definitions (New in v0.0.7)

So these are really fun, especially if you are a functional programmer at heart...

``` python

my_definition = {
	'email': ['require', ('alt', 'email_address'), 'email'], # email address with alternate name
	'age': ['require', 'numeric', ('range', 13, 100)] # age must be numeric between 13 and 100
	'password': [('text', 10, 50)],
	'passwordConfirm': [('match', 'password')]
}

s = Schema.from_dict(my_definition)
s.validate(some_data) # Bam!

```

I know, really cool. Also probably really confusing if you didn't spot the pattern right away...

Explanation: keys are field names, options follow in a list. If you want to call an option without arguments, simply specify it as a string. If you want to call an option (filter or modifier) with arguments, you use a tuple.

For example, the following two blocks are equivalent:

``` python

s = Schema()
s.my_happy_place.require().text(min_len=15, max_len=25)

```

same as

``` python

sdict = {
	'my_happy_place': ['require', ('text', 15, 25)]
}

s = Schema.from_dict(sdict)

```

The only and obvious downside of dict-based definitions is that they require you to know the argument order of most of the filters. Luckily, most filters do not even take arguments and the ones that do are fairly obvious / intuitive / documented :)

The ``` from_dict ``` method takes ``` **kwargs ``` so you can just pass your Schema level options like ``` force_unicode=True ``` there.

## Filters (validators)

There are currently 42 filter functions (validators) in this library. They are spread across modules categorically, but all end up in the same namespace because of the dynamic lookup system used for the API. This is not really much of an issue, since the filters use (and will continue to use) non-ambiguous names.

The list of filters is as follows, by category:

### Web
* email
* ipv4
* url
* uri
* cidr4
* cidr6
* macaddress

### Money
* credit_card(brands=[])

### Strings
* text
* alphanumeric
* alpha
* numeric_string
* nonblank
* removespaces
* strip
* lower
* upper
* regex
* canonize
* slugify

### Numerical
* range(low, high)
* minimum(number)
* maximum(number)
* between(low, high)
* equal(number)
* zero

### Logical
* constant

### Constant
* drop_keys
* contains

### Chrono
* date(format='%m/%d/%Y')
* time(format='%I:%M:%S')
* datetime(format='%m/%d/%Y %I:%M:%S')
* time_before(deadline)
* time_after(milestone)
* time_between(milestone, deadline)

### Casting
* boolean
* strbool
* integer
* longint
* numeric
* string
* none