from tgext.datahelpers.caching import cached_query
import sqla_base as sqlabase
import tg
import beaker
from nose.tools import raises
from sqlalchemy.orm.exc import MultipleResultsFound

class TestCachedQuery(object):
    def __init__(self):
        class FakeCache(object):
            def __init__(self):
                self._cache = {}
            def get_cache(self, *args, **kw):
                return self
            def get_value(self, key, createfunc, *args, **kw):
                if key not in self._cache:
                    self._cache[key] = createfunc()
                return self._cache[key]
        self.cache = FakeCache()

    def setup(self):
        self._tg_cache = tg.cache
        tg.cache = self.cache
        sqlabase.setup_database()
        sqlabase.clear_database()
        tg.config['DBSession'] = sqlabase.DBSession

    def teardown(self):
        tg.cache = self._tg_cache
        sqlabase.clear_database()

    def test_cache_all(self):
        mo = sqlabase.ThingWithDate(name=u'something')
        sqlabase.DBSession.add(mo)
        sqlabase.DBSession.flush()
        sqlabase.DBSession.commit()

        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).all()

        assert len(q) == 1
        assert q[0].name == mo.name
        cached_result = q[0]

        #run query again to check it is has actually been cached
        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).all()

        assert len(q) == 1
        assert q[0] is cached_result

    def test_cache_iter(self):
        mo = sqlabase.ThingWithDate(name=u'something')
        sqlabase.DBSession.add(mo)
        sqlabase.DBSession.flush()
        sqlabase.DBSession.commit()

        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate))

        for e in q:
            assert e.name == mo.name
            break

    def test_cache_first(self):
        mo = sqlabase.ThingWithDate(name=u'something')
        sqlabase.DBSession.add(mo)
        sqlabase.DBSession.flush()
        sqlabase.DBSession.commit()

        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).first()

        assert q is not None
        assert q.name == mo.name
        cached_result = q

        #run query again to check it is has actually been cached
        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).first()

        assert q is not None
        assert q is cached_result

    def test_cache_first_noresult(self):
        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).first()
        assert q is None

        mo = sqlabase.ThingWithDate(name=u'something')
        sqlabase.DBSession.add(mo)
        sqlabase.DBSession.flush()
        sqlabase.DBSession.commit()

        #run query again to check it is has actually been cached
        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).first()
        assert q is not None

    def test_cache_one(self):
        mo = sqlabase.ThingWithDate(name=u'something')
        sqlabase.DBSession.add(mo)
        sqlabase.DBSession.flush()
        sqlabase.DBSession.commit()

        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).one()

        assert q is not None
        assert q.name == mo.name
        cached_result = q

        #run query again to check it is has actually been cached
        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).one()

        assert q is not None
        assert q is cached_result

    def test_cache_one_noresult(self):
        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).first()
        assert q is None

        mo = sqlabase.ThingWithDate(name=u'something')
        sqlabase.DBSession.add(mo)
        sqlabase.DBSession.flush()
        sqlabase.DBSession.commit()

        #run query again to check it is has actually been cached
        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).one()
        assert q is not None

    @raises(MultipleResultsFound)
    def test_cache_one_multiple_results(self):
        sqlabase.DBSession.add(sqlabase.ThingWithDate(name=u'something'))
        sqlabase.DBSession.add(sqlabase.ThingWithDate(name=u'something2'))
        sqlabase.DBSession.flush()
        sqlabase.DBSession.commit()

        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).all()
        assert len(q) == 2

        #run query again to check it is has actually been cached and one is used
        q = cached_query('samplequery',
                         sqlabase.DBSession.query(sqlabase.ThingWithDate)).one()


class TestFileCachedQuery(TestCachedQuery):
    """
    This is to check it works as expected on cache backends that pickle
    the query data
    """
    def __init__(self):
        class FileCache(object):
            def get_cache(self, *args, **kw):
                return beaker.cache.Cache(type='file', data_dir='.', *args, **kw)
        self.cache = FileCache()
