# confypy

Python **2.6**, **2.7**, **3.2** and **3.3** compatible

## Simple Configuration Loading and Management


## Usage

Once a config is configured with locations, it's values are accessed through
the `data` attribute. Key or Attribute access is valid:

```python
from confypy import Config
from confypy import Location

config = Config()
config.locations = [Location.from_env_keys(['FOO', 'BAR', 'BAZ'])]

print(config.data.FOO)
print(config.data.BAR)
print(config.data.BAZ)

# OR

print(config.data['FOO'])
print(config.data['BAR'])
print(config.data['BAZ'])

```

## Built-In Parsers
By *built-in*, we mean confypy will automatically check for common
config parsers of the following types:

- json (falls back to simplejson)
- yaml (pyyaml required)
- configparser (Python's own ConfigParser)
- python (load a module's __dict__)

It determines the parser to use by checking the file extension of
any file paths. However, you are also free to override this.

The parser can manually be set in the Location.* declaration.

For example, each of the following assumes JSON:

```python
Location.from_path('/data/foo.json')
```

So does this:
```python
Location.from_path('/data/foo', parser='json')
```

And so does this:

```python
import json
Location.from_path('/data/foo', parser=json.loads)
```

And this too:
*Note that the imported 'json' here is just a reference to the json.loads callable*

```python
import json
from confypy import Location
from confypy.loaders import load_file
from confypy.parsers import json

location = Location('data/foo', loader=load_file, parser=json)

```

Yes, the parser argument to Location can be a `string` OR a `callable`.
In fact, the various Location.* factories just handle passing the parser
arg for you.

Parsers are chosen from strings and file extensions with the following
rules: (see confypy.parsers.parser_for_ext)

```python
def parser_for_ext(ext):

    mapping = {
    'yml': yaml,
    'yaml': yaml,
    'json': json,
    'ini': configparser,
    'configparser': configparser
    }

    result = mapping.get(ext.lower(), None)

    if result:
        return result

    raise ParserNotFound(ext)
```


## Defaults

Each config supports a set of defaults provided at creation time.

```python
from confypy import Config
from confypy import Location


defaults = {'foo':1, 'bar':2, 'baz':3}
config = Config(defaults=defaults)
```

If no locations are present, or if none of the locations, when loaded, return
any valid data, the defaults will be when looking up values.

When locations are chained, the defaults represent the last location for a
lookup before an error is raised.


## Examples


#### Stop loading after the 1st successful load.

In the example below, the `TEST_SETTINGS` environment variable will be
checked first. It's assumed that it's value will be a file path:
`from_env_path`. It's also possible to just load environment variables
as key/values which will follow in another example.

So `TEST_SETTINGS` will be checked first, if the file exists, the drama
stops there. If it doesn't exist, it moves on to the next Location
provided in the locations list.

Assuming our file contains this JSON:

```json
{
    "name": "Lucy"
}
```

We can do this:

```python
from confypy import Config
from confypy import Location

config = Config()
config.locations = [
    Location.from_env_path('TEST_SETTINGS'),
    Location.from_path('/data/foo.json')
]

print(config.data.name)
```

#### Try to load everything and chain the results together.

The resultant config can be chained. Values will be looked up starting
from the last location provided in the locations list, falling **up**
to the first location provided in the location list.

In other words the lookup order is like this in a chain:

```python
from confypy import Config
from confypy import Location

config = Config(chain=True)
config.locations = [
    Location.from_env_path('TEST_SETTINGS'),       # 5
    Location.from_path('/data/foo.json'),          # 4 ^
    Location.from_path('/data/foo.yaml'),          # 3 ^
    Location.from_env_keys(['FOO', 'BAR', 'BAZ']), # 2 ^
    Location.from_python('path.to.my.module')      # 1 ^
]
```

In order to get this chaining, the `Config` must be initialized with the
argument `chain=True`
