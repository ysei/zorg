import sqlalchemy
import testsuite
import testsuitedb

class V4DB(object):
    """
    Wrapper object for LNT v0.4+ databases.
    """

    class TestSuiteAccessor(object):
        def __init__(self, v4db):
            self.v4db = v4db

        def __iter__(self):
            for name, in self.v4db.query(testsuite.TestSuite.name):
                yield name

        def __getitem__(self, name):
            # Get the test suite object.
            ts = self.v4db.query(testsuite.TestSuite).\
                filter(testsuite.TestSuite.name == name).first()
            if ts is None:
                raise IndexError,name

            # Instantiate the per-test suite wrapper object for this test suite.
            return testsuitedb.TestSuiteDB(self.v4db, ts)

        def keys(self):
            return iter(self)

        def values(self):
            for name in self:
                yield self[name]

        def items(self):
            for name in self:
                yield name,self[name]

    def __init__(self, path, echo=False):
        # If the path includes no database type, assume sqlite.
        #
        # FIXME: I would like to phase this out and force clients to propagate
        # paths, but it isn't a big deal.
        if not path.startswith('mysql://') and not path.startswith('sqlite://'):
            path = 'sqlite:///' + path

        self.path = path
        self.engine = sqlalchemy.create_engine(path, echo=echo)

        # Create the common tables in case this is a new database.
        testsuite.Base.metadata.create_all(self.engine)

        self.session = sqlalchemy.orm.sessionmaker(self.engine)()

        # Add several shortcut aliases.
        self.add = self.session.add
        self.commit = self.session.commit
        self.query = self.session.query

    @property
    def testsuite(self):
        # This is the start of "magic" part of V4DB, which allows us to get
        # fully bound SA instances for databases which are effectively described
        # by the TestSuites table.

        # The magic starts by returning a object which will allow us to use
        # dictionary like access to get the per-test suite database wrapper.
        return V4DB.TestSuiteAccessor(self)

    # FIXME: The getNum...() methods below should be phased out once we can
    # eliminate the v0.3 style databases.
    def getNumMachines(self):
        return sum([ts.query(ts.Machine).count()
                    for ts in self.testsuite.values()])
    def getNumRuns(self):
        return sum([ts.query(ts.Run).count()
                    for ts in self.testsuite.values()])
    def getNumSamples(self):
        return sum([ts.query(ts.Sample).count()
                    for ts in self.testsuite.values()])
    def getNumTests(self):
        return sum([ts.query(ts.Test).count()
                    for ts in self.testsuite.values()])

    def importDataFromDict(self, data):
        raise NotImplementedError
