
# Schema extractor for MongoDB

Mongo-inspector is a Python library that analyses the data of a MongoDB
database to extract its "schema" (I know...).

## Installation

    $ pip install mongo-inspector

## Usage

    import mongo_inspector
    schema = mongo_inspector.extract_schema(
        db_name='mydb',
        host='myhost',  # optional: default 'localhost'
        port=xxxx       # optional: default 27017
    )

The returned schema looks like that:

    {
        u'SomeCollection': [
            Attribute(name=u'id', types=[u'String']),
            Attribute(name=u'someattribute', types=[u'String'])
        ],
        u'AnotherCollection': [
            Attribute(name=u'_id', types=[u'ObjectId']),
            Attribute(name=u'someattr', types=[u'Object']),
            Attribute(name=u'someattr.nested', types=[u'Number']),
            Attribute(name=u'somelist', types=[u'Array']),
            Attribute(name=u'somelist.__item__', types=[u'Object']),
            Attribute(name=u'somelist.__item__.nested',
                      types=[u'String', u'Number'])
        ]
    }

`Attribute(name, types)` is just a `nametuple`. Each attribute can have
several types.

## Future

* It might be usefull to return a tree instead of 'point-separated'
  nested keys.
