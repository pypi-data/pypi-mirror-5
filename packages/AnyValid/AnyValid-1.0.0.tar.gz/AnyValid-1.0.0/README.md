Any Valid
=========
The AnyValid class is a wrapper class to be used with, for example, [formencode.validators](http://www.formencode.org/en/latest/modules/validators.html#module-formencode.validators), that lets you partially specify what kind of objects it should match.  To see the usefulness of this, it might be easier to first have a look at mock's ANY object ([from unittest.mock's documentation](http://docs.python.org/3/library/unittest.mock.html#any)):

> Sometimes you may need to make assertions about some of the arguments in a call to mock, but either not care about some of the arguments or want to pull them individually out of call_args and make more complex assertions on them.

> To ignore certain arguments you can pass in objects that compare equal to everything. Calls to assert_called_with() and assert_called_once_with() will then succeed no matter what was passed in.

> ```python
>>>
>>> mock = Mock(return_value=None)
>>> mock('foo', bar=object())
>>> mock.assert_called_once_with('foo', bar=ANY)
```
> ANY can also be used in comparisons with call lists like mock_calls:
> ```python
>>>
>>> m = MagicMock(return_value=None)
>>> m(1)
>>> m(1, 2)
>>> m(object())
>>> m.mock_calls == [call(1), call(1, 2), ANY]
True
```

Now, what if you would like to make certain assertions about an argument, but perhaps don't know the exact value, or want to avoid certain values (for example ```None```).  This is where AnyValid might come in handy.  It provides a really simple way to leverage all the great work that has been put into formencode's validators, so that your testing code can make advanced assertions while being easy to read and maintain.

Examples
========
Simple argument matching:
```python
>>>
>>> from mock import Mock
>>> from any_valid import AnyValid, Int, String
>>>
>>> def check_call(foo, bar):
...     try:
...         mock = Mock(return_value=None)
...         mock(foo, bar=bar)
...         mock.assert_called_once_with(AnyValid(String(min_lenght=3)), 
...                                      bar=AnyValid(Int(min=2)))
...     except AssertionError:
...         return False
...     return True
... 
>>> check_call('fo', 1)
False
>>> check_call(8, 0)
False
>>> check_call('foo', 2)
True
```

Matching a loosely defined dict argument:
```python
>>> from any_valid import AnyValid, Number, OneOf
>>> valid_input = {
...     'core_temperature': AnyValid(Number(min=35, max=41.5)),
...     'protocol': AnyValid(OneOf(['https', 'http'])),
...     }
>>> mock = Mock(return_value=None)
>>> mock({'core_temperature': 36.8, 'protocol': 'https'})
>>> mock.assert_called_with(valid_input)
>>>
```


