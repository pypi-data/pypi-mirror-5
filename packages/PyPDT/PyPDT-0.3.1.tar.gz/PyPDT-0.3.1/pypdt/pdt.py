# -*- python -*-

"Pythonic access to high energy particle data tables."


C_IN_MM_PER_PS = 0.299792458
HBAR_IN_GEVPS = 6.58211814E-13


def lifetime_to_width(tau): # tau in picoseconds
    "Convert a lifetime, tau, in picoseconds, to a width in GeV"
    if not tau:
        return None
    return HBAR_IN_GEVPS/float(tau)

def width_to_lifetime(gamma): # gamma in GeV
    "Convert a width, gamma, in GeV, to a lifetime in picoseconds"
    if not gamma:
        return None
    return HBAR_IN_GEVPS/float(gamma)


class LorentzViolation(Exception):
    "An exception thrown when a condition inconsistent with special relativity is encountered."
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self):
        return "Lorentz consistency has been violated: " + self.msg


class ParticleData(object):
    """
    Container for a few particle data properties. Its main job is to resolve
    which of lifetime vs. width to use for a given particle.

    A string representation is defined for convenience.

    The available properties are id, name, mass, threecharge, charge, width,
    lifetime, and ctau. The mean displacement in vacuum for a supplied energy is
    accessed via the mean_disp(energy) method.
    """

    def __init__(self, id, name, mass, threecharge, width=None, lifetime=None):
        assert id is not None
        self.id = int(id)
        assert name is not None
        self.name = name
        assert mass is not None
        self.mass = float(mass)
        assert threecharge is not None
        self.threecharge = threecharge
        if not lifetime and width is None:
            self._lifetime = None
            self._width = None
        elif not lifetime: # width = 0 overrides lifetime = 0
            self.set_width(width)
        else:
            self.set_lifetime(lifetime)

    @property
    def charge(self):
        return self.threecharge / 3.0

    def get_lifetime(self):
        "Get the particle lifetime in picoseconds."
        return self._lifetime
    def set_lifetime(self, tau):
        "Set the particle lifetime (and, implicitly, the width). tau is lifetime in picoseconds."
        self._lifetime = tau
        self._width = lifetime_to_width(tau)
    lifetime = property(get_lifetime, set_lifetime)

    def get_width(self):
        "Get the particle width in GeV."
        return self._width
    def set_width(self, gamma):
        "Set the particle width (and, implicitly, the lifetime). gamma is width in GeV."
        self._lifetime = width_to_lifetime(gamma)
        self._width = gamma
    width = property(get_width, set_width)

    @property
    def ctau(self):
        "Get the particle c tau distance in mm."
        if self.lifetime is None:
            return None
        return self.lifetime * C_IN_MM_PER_PS

    def mean_disp(self, energy):
        "Get the particle mean displacement in mm, for the given particle energy in GeV (includes Lorentz boost factor)."
        if self.lifetime is None:
            return None
        if energy < self.mass:
            raise LorentzViolation("energy %1.2f GeV less than particle mass %1.2f GeV for PID = %d" % (energy, self.mass, self.id))
        from math import sqrt
        gamma = float(energy) / self.mass
        beta = sqrt(1.0 - gamma**-2)
        #print beta, gamma
        return self.ctau * beta * gamma

    def __repr__(self):
        s = "%s: ID=%d, m=%1.2e GeV, 3*q=%d" % (self.name, self.id, self.mass, self.threecharge)
        if self.width is not None:
            s += ", width=%1.2e GeV" % self.width
        if self.lifetime is not None:
            s += ", tau=%1.2e ps" % self.lifetime
        if self.ctau is not None:
            s += ", ctau=%1.2e mm" % self.ctau
        return s


## Add PID functions to the ParticleData object as bound methods
import pypdt.pid as _PID
for symname in dir(_PID):
    if not symname.startswith("_") and not symname.startswith("N"):
        ## Note lambda binding / lexical closure trick with sym=
        f = lambda self, sym=getattr(_PID, symname) : sym(self.id)
        setattr(ParticleData, symname, f)


class ParticleDataTable(object):
    """
    Wrapper object for a whole database of ParticleData objects, indexed by their PDG ID codes.

    By default, the input database file will be the particle.tbl file from the most recent HepPDT
    version (3.04.01), accessed via the CERN AFS filesystem. If you want a different db file, or
    don't have AFS mounted, specify an explicit file path.
    """

    def __init__(self, dbpath=None):
        """
        Constructor, taking the path to the PDT database file as an argument.
        If no arg is supplied, or it is None, try to find and load the version
        installed by the package, or fall back to look at $PYPDT_DB or on CERN AFS.
        """
        import os
        if dbpath is None:
            ## If no path specified, try first the local then the AFS db files
            prefix = os.path.dirname(__file__)
            for i in xrange(4): # remove 4 directory levels
                prefix = os.path.dirname(prefix)
            dbpath = os.path.join(prefix, "share", "pypdt", "particle.tbl")
            if not os.path.exists(dbpath):
                if os.environ.has_key("PYPDT_DB"):
                    dbpath = os.environ["PYPDT_DB"]
                else:
                    dbpath = "/afs/cern.ch/sw/lcg/external/HepPDT/3.04.01/src/HepPDT-3.04.01/data/particle.tbl"
        self.clear()
        self.read_db(dbpath)

    def clear(self):
        "Forget all currently known particles."
        self.entries = {}
        self.dbfiles = []

    def read_db(self, dbpath):
        """Read a particle data database file, updating the currently registered
        particles. Call clear() first if you *only* want to know about the
        particle data in this db file. The db files currently in use can be
        access via the PDT.dbfiles attribute."""
        self.dbfiles.append(dbpath)
        dbf = open(dbpath)
        for line in dbf:
            ## Handle comments
            if "//" in line:
                line = line[:line.find("//")]
            line = line.strip()
            if not line:
                continue
            data = line.split()
            #print data

            ## Parse a data line
            pid = int(data[0])
            name = data[1]
            threecharge = int(data[2])
            mass = float(data[3])
            width = float(data[4])
            lifetime = float(data[5])

            ## Add a ParticleData object into the entries dict for this PID
            self.entries[pid] = ParticleData(pid, name, mass, threecharge, width, lifetime)
        dbf.close()

    def ids(self):
        """Get the list of known particle IDs (using the PDG Monte Carlo numbering
        scheme). These are the available keys for db lookup."""
        return self.entries.keys()

    def has_key(self, id):
        """Check if the PDT contains particle data for the supplied particle
        ID. Alternatively usable as has_particle(id)."""
        return self.entries.has_key(int(id))

    "A HEP-ish alias for has_key()"
    has_particle = has_key

    def get(self, id, default=None):
        """Get the particle data for the supplied particle ID. Alternatively
        usable as particle(id, default) or tbl[id]."""
        return self.entries.get(int(id), default)

    "A HEP-ish alias for get()"
    particle = get

    """'Square bracket' access to particles in the table by PID code. Returns
    None rather than throwing an exception if the requested PID does not exist
    in the table."""
    __getitem__ = particle

    def __iter__(self):
        "Iterate over all known particles, yielding a ParticleData for each iteration."
        for pd in self.entries.values():
            yield pd


"Super-short alias for the rather lengthy ParticleDataTable class"
PDT = ParticleDataTable


def get(pid, dbpath=None):
    """Get the ParticleData object for particle ID pid, looked up using the
    ParticleDataTable constructed with db file argument dbpath."""
    return PDT().get(pid, None)

"A HEP-ish alias for get()"
particle = get

#print "#", get(2212).isValid(), get(2212).threeCharge(), get(2212).charge()
