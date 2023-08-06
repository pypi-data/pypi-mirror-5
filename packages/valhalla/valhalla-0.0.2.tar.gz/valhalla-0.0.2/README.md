==========
Valhalla
==========

-----------

This is a very minimalist Python data validation and filtering library.

There are many libraries for this sort of thing in many languages, what
makes this one special is the ease and brevity of the API. Data validation
by nature is a rather tedious and manual task that requires the programmer
to define explicitly the data points being filtered and how to do it.

The goal of this library was to make that explicitness as painless as possible.

The API is designed to afford the programmer the least amount of typing for each
use case, with the option to be more verbose when necessary.


Straight to business...

```python

# Minimalist schema

s = Schema()
s.first_name.text()
s.last_name.text()
s.email.email()

s.validate({
	'first_name': 'Peter',
	'last_name': 'Elias',
	'email': 'petermelias@gmail.com'
})

print s.valid # True

# More involved schema

s = Schema()
s.first_name(req=True).text(min_len=1, max_len=255).capfirst() # required field, length enforcement, captialize first letter of first word
s.last_name(alt='last_name_input').initial() # detect alternate input field name, truncate to initials

s.validate({
	'last_name_input': 'Norris'
})

print s.valid # False

print s.first_name.valid # False
print s.first_name.errors # ['Required field']
print s.last_name.valid # True -- works because alternate names refer to the same validator as the original field name
print s.last_name.result # ('Norris', 'N') -- prints original value and then processed value

# Schemas can be reset and used again with new data

new_data = {
	'first_name': 'Darth',
	'last_name': 'Vader',
	'email': 'force@choke.com'
}

s.reset()
s.validate(new_data)
```

The validator functions themselves are kept in the ```filters``` package. They are organized
into modules that serve to categorize their purpose. It should be noted that the modular separation
is not to guarantee namespacing (as is traditional with Python modules) because the lookup system
assumes that each function has a unique name in order to keep the API nice and short.

To reiterate, all validation functions, despite being in separate modules, must have unique names
or they will be ignored by the lookup system when it finds the first one with a given name.

More examples, filter functions and documentation to follow soon.