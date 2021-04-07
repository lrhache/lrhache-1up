from typing import TypeVar, Union, Generator, Type, cast
from collections import defaultdict
from dataclasses import dataclass, field

from exceptions import DuplicateDocument, ResourceNotDefined


__all__ = ['create_document']


T = TypeVar('T')


def create_document(data: dict) -> T:
    """ Helper to create a document from the data received

    Required keys:
        resourceType: Corresponding to a defined model
        id: Unique identifier
    """
    assert 'resourceType' in data
    assert 'id' in data

    resource_type = data['resourceType']
    document_id = data['id']

    base_cls = MetaBaseModel.registered_class.get(resource_type)

    if not base_cls:
        raise ResourceNotDefined(resource_type)

    return base_cls['self'](id=document_id, data=data)


class MetaBaseModel(type):
    """ Metaclass used for all the models

    - Registers the model types (based on resourceType)
    - Create search indexes
    - Create back references
    - Provide search functions as class methods to all models

    References:
        The references are objects referenced in a model.
        IE: {patient: {reference: 'Patient/uniqueid'}
        IE: {member: [{entity: {reference: 'Patient/uniqueid'}}}

        The references can be specified in a dotkey notation in the model
        IE: reference = ['patient']
        IE: reference = ['member.entity']

    Search Indexes:
        The search indexes are specified in the model in a dotkey notation.
        IE: ['name.given', 'name.family']
    """

    # keep a registry of all the models we have available
    registered_class: dict = {}

    # search index by terms/keywords
    index_terms: list = []

    # search index by id key
    index_id: dict = {}

    # keep track of back references if the instance is not created yet
    _back_references: dict = defaultdict(list)

    def __new__(metacls: Type['MetaBaseModel'],
                clsname: str, bases: tuple,
                classdict: dict) -> 'MetaBaseModel':
        cls = super().__new__(metacls, clsname, bases, classdict)
        metacls.registered_class[clsname] = {
            'self': cls,
            'references': classdict.get('references')
        }

        return cast(MetaBaseModel, cls)

    def __call__(cls, *args: list, **kwargs: dict) -> T:
        # Get the modelname and registered configs
        registered_class = MetaBaseModel.registered_class[super().__name__]

        document_id = str(kwargs['id']).lower()
        if MetaBaseModel.index_id.get(document_id):
            raise DuplicateDocument(
                MetaBaseModel.index_id[document_id], document_id)

        instance = super().__call__(*args, **kwargs)

        MetaBaseModel.index_instance(instance, kwargs['data'])

        if references := MetaBaseModel._back_references.get(document_id):
            # set the references from previously loaded models
            instance.set_referenced(*references)

            for referenced_instance in references:
                referenced_instance.set_references(instance)

            del MetaBaseModel._back_references[document_id]

        if registered_class['references']:
            MetaBaseModel.set_references(
                instance, kwargs['data'], registered_class['references'])

        MetaBaseModel.index_id[document_id] = instance
        return instance

    @classmethod
    def index_instance(cls, instance: T, data: dict) -> None:
        """ Create the search indexes for a model instance """
        if not hasattr(instance, 'index'):
            # if the index attribute is not set in the model
            # there's nothing to do
            return

        terms = [data['id']]        # include the ID in all search indexes
        for key_name in instance.index:
            keys = key_name.split('.')
            values = MetaBaseModel.find_key(data, keys)

            if values is None:
                continue

            if not isinstance(values, list):
                values = [values]

            terms += values

        index_terms = ' '.join([str(w).lower() for w in {terms}])
        MetaBaseModel.index_terms.append((instance, index_terms))

    @classmethod
    def set_references(cls, instance: T,
                       data: dict, references: list) -> None:
        """ Set the back references for an instance """

        for key_name in references:
            keys = key_name.split('.')
            values = MetaBaseModel.find_key(data, keys)

            if values is None:
                continue

            if not isinstance(values, list):
                values = [values]

            for reference in values:
                if 'reference' not in reference:
                    # TODO: something went wrong, log it
                    continue

                model_name, document_id = reference['reference'].split('/')

                if model := cls.index_id.get(document_id):
                    instance.set_references(model)
                    model.set_referenced(instance)
                else:
                    # the model instance doesn't exists, keep a cache
                    # and load the references once the instance is initated
                    cls._back_references[document_id].append(instance)

    def get(cls, document_id: str) -> Union[T, None]:
        """ Get a single document by ID """
        document_id = str(document_id).lower()

        if result := MetaBaseModel.index_id.get(document_id):

            if type(result).__name__ == cls.__name__:
                return result

        # raise ResultNotFound(cls, document_id)
        return None

    def find(cls, search_terms: Union[list, str]) -> Generator[T, None, None]:
        """ Find a set of document matching the search terms

        Example:
            Return patients containing Abernathy in the search index
            Patient.find('Abernathy')
        """
        if not isinstance(search_terms, (list, tuple)):
            search_terms = str(search_terms).split(' ')

        search_terms = [str(s).strip().lower()
                        for s in search_terms if str(s).strip()]

        for instance, index in MetaBaseModel.index_terms:
            if type(instance).__name__ != cls.__name__:
                continue

            if all(term in index for term in search_terms):
                # execute a basic word match within the index
                yield instance

    @staticmethod
    def find_key(d: Union[dict, list], keys: list) -> Union[list[T], T, None]:
        """ Traverse a set of keys and return the value

        Example:
            keys = ['a', 'b', 'c']
            data (d) = {'a': {'b': [{'c': 1}, {'c': 2}]}
            return [1, 2]

            keys = ['a', 'b', 'c']
            data (d) = {'a': {'b': {'c': 1}}
            return 1
        """
        if len(keys) <= 1 or (isinstance(d, dict) and not d.get(keys[0])):
            return d.get(keys[0]) if isinstance(d, dict) else None

        if isinstance(d[keys[0]], list):
            results = []
            for o in d[keys[0]]:
                result = MetaBaseModel.find_key(o, keys[1:])
                if result is None:
                    continue

                if isinstance(result, list):
                    for r in result:
                        results.append(r)
                else:
                    results.append(result)

            return results

        else:
            result = MetaBaseModel.find_key(d[keys[0]], keys[1:])
            if result is not None:
                return result

            return None


@dataclass
class BaseModel(metaclass=MetaBaseModel):
    id: str
    data: dict = field(repr=False)

    # back reference models (parents)
    # this attribute will hold all instances where this instance is referenced
    _referenced: set = field(default_factory=set, init=False, repr=False)

    # referenced models (children)
    # this attribute will hold all instances referenced in this model
    _references: set = field(default_factory=set, init=False, repr=False)

    def set_references(self, *references: tuple) -> None:
        self._references |= set(references)

    def set_referenced(self, *referenced: tuple) -> None:
        self._referenced |= set(referenced)

    def traverse_references(self, references) -> set:
        """ Get all references with optionally traversing all children """
        _references = set()

        for reference in references:
            _references |= reference.traverse_references(reference._references)

        return references | _references

    def get_connections(self) -> defaultdict[str, set]:
        connections = defaultdict(set)

        all_connections = self.traverse_references(self._references)
        all_connections |= self.traverse_references(self._referenced)

        for connection in all_connections:
            if connection != self:
                connections[type(connection).__name__].add(connection)

        return connections

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
