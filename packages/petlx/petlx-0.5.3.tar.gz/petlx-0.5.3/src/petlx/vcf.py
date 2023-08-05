from __future__ import absolute_import # avoid module name clash with pyvcf
from petl.util import RowContainer
from petl import unpackdict, melt, convert, rename
from petlx.util import UnsatisfiedDependency


dep_message = """
The package vcf is required. Instructions for installation can be found 
at https://pypi.python.org/pypi/PyVCF or try pip install PyVCF.
"""


def fromvcf(filename, chrom=None, start=None, end=None, samples=True):
    """
    Returns a table providing access to data from a variant call file (VCF). E.g.::
    
        >>> from petl import look
        >>> from petlx.vcf import fromvcf
        >>> t = fromvcf('example.vcf')
        >>> look(t)
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
        | 'CHROM' | 'POS'   | 'ID'        | 'REF' | 'ALT'     | 'QUAL' | 'FILTER' | 'INFO'                                                                                  | 'NA00001'                                                           | 'NA00002'                                                        | 'NA00003'                                                            |
        +=========+=========+=============+=======+===========+========+==========+=========================================================================================+=====================================================================+==================================================================+======================================================================+
        | '19'    |     111 | None        | 'A'   | [C]       |    9.6 | []       | {}                                                                                      | Call(sample=NA00001, CallData(GT=0|0, HQ=[10, 10]))                 | Call(sample=NA00002, CallData(GT=0|0, HQ=[10, 10]))              | Call(sample=NA00003, CallData(GT=0/1, HQ=[3, 3]))                    |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
        | '19'    |     112 | None        | 'A'   | [G]       |     10 | []       | {}                                                                                      | Call(sample=NA00001, CallData(GT=0|0, HQ=[10, 10]))                 | Call(sample=NA00002, CallData(GT=0|0, HQ=[10, 10]))              | Call(sample=NA00003, CallData(GT=0/1, HQ=[3, 3]))                    |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
        | '20'    |   14370 | 'rs6054257' | 'G'   | [A]       |     29 | []       | OrderedDict([('NS', 3), ('DP', 14), ('AF', [0.5]), ('DB', True), ('H2', True)])         | Call(sample=NA00001, CallData(GT=0|0, GQ=48, DP=1, HQ=[51, 51]))    | Call(sample=NA00002, CallData(GT=1|0, GQ=48, DP=8, HQ=[51, 51])) | Call(sample=NA00003, CallData(GT=1/1, GQ=43, DP=5, HQ=[None, None])) |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
        | '20'    |   17330 | None        | 'T'   | [A]       |      3 | ['q10']  | OrderedDict([('NS', 3), ('DP', 11), ('AF', [0.017])])                                   | Call(sample=NA00001, CallData(GT=0|0, GQ=49, DP=3, HQ=[58, 50]))    | Call(sample=NA00002, CallData(GT=0|1, GQ=3, DP=5, HQ=[65, 3]))   | Call(sample=NA00003, CallData(GT=0/0, GQ=41, DP=3, HQ=[None, None])) |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
        | '20'    | 1110696 | 'rs6040355' | 'A'   | [G, T]    |     67 | []       | OrderedDict([('NS', 2), ('DP', 10), ('AF', [0.333, 0.667]), ('AA', 'T'), ('DB', True)]) | Call(sample=NA00001, CallData(GT=1|2, GQ=21, DP=6, HQ=[23, 27]))    | Call(sample=NA00002, CallData(GT=2|1, GQ=2, DP=0, HQ=[18, 2]))   | Call(sample=NA00003, CallData(GT=2/2, GQ=35, DP=4, HQ=[None, None])) |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
        | '20'    | 1230237 | None        | 'T'   | [None]    |     47 | []       | OrderedDict([('NS', 3), ('DP', 13), ('AA', 'T')])                                       | Call(sample=NA00001, CallData(GT=0|0, GQ=54, DP=None, HQ=[56, 60])) | Call(sample=NA00002, CallData(GT=0|0, GQ=48, DP=4, HQ=[51, 51])) | Call(sample=NA00003, CallData(GT=0/0, GQ=61, DP=2, HQ=[None, None])) |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
        | '20'    | 1234567 | 'microsat1' | 'G'   | [GA, GAC] |     50 | []       | OrderedDict([('NS', 3), ('DP', 9), ('AA', 'G'), ('AN', 6), ('AC', [3, 1])])             | Call(sample=NA00001, CallData(GT=0/1, GQ=None, DP=4))               | Call(sample=NA00002, CallData(GT=0/2, GQ=17, DP=2))              | Call(sample=NA00003, CallData(GT=None, GQ=40, DP=3))                 |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
        | '20'    | 1235237 | None        | 'T'   | [None]    | None   | []       | {}                                                                                      | Call(sample=NA00001, CallData(GT=0/0))                              | Call(sample=NA00002, CallData(GT=0|0))                           | Call(sample=NA00003, CallData(GT=None))                              |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
        | 'X'     |      10 | 'rsTest'    | 'AC'  | [A, ATG]  |     10 | []       | {}                                                                                      | Call(sample=NA00001, CallData(GT=0))                                | Call(sample=NA00002, CallData(GT=0/1))                           | Call(sample=NA00003, CallData(GT=0|2))                               |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+---------------------------------------------------------------------+------------------------------------------------------------------+----------------------------------------------------------------------+
    
    .. versionadded:: 0.5
    
    """
    return VCFContainer(filename, chrom=chrom, start=start, end=end, samples=samples)


fixed_fields = 'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO'


class VCFContainer(RowContainer):

    def __init__(self, filename, chrom=None, start=None, end=None, samples=True):
        self.filename = filename
        self.chrom = chrom
        self.start = start
        self.end = end
        self.samples = samples
        
    def __iter__(self):
        try:
            import vcf as pyvcf
        except ImportError as e:
            raise UnsatisfiedDependency(e, dep_message)
        reader = pyvcf.Reader(filename=self.filename)
        
        # determine header
        if isinstance(self.samples, (list, tuple)):
            # specific samples requested
            yield fixed_fields + tuple(self.samples)
        elif self.samples:
            # all samples
            yield fixed_fields + tuple(reader.samples)
        else:
            # no samples
            yield fixed_fields
            
        # fetch region?
        if None not in {self.chrom, self.start, self.end}:
            it = reader.fetch(self.chrom, self.start, self.end)
        else:
            it = reader
            
        # yield data
        for rec in it:
            out = tuple(getattr(rec, f) for f in fixed_fields)
            if isinstance(self.samples, (list, tuple)):
                # specific samples requested
                out += tuple(rec.genotype(s) for s in self.samples)
            elif self.samples:
                # all samples
                out += tuple(rec.samples)
            yield out
            
            
class VCFWrapper(RowContainer):
    
    def __init__(self, inner, filename):
        object.__setattr__(self, 'filename', filename)
        object.__setattr__(self, '_inner', inner)

    def __iter__(self):
        return iter(self._inner)

    def __getattr__(self, attr):
        # pass through
        return getattr(self._inner, attr) 
    
    def __setattr__(self, attr, value):
        # pass through
        setattr(self._inner, attr, value)
        
    def __getitem__(self, item):
        # pass through
        return self._inner[item]
    
    def __setitem__(self, item, value):
        # pass through
        self._inner[item] = value

    def __str__(self):
        return str(self._inner)

    def __repr__(self):
        return repr(self._inner)

            
def unpackinfo(tbl, *keys, **kwargs):
    """
    Unpack the INFO field into separate fields. E.g.::

        >>> from petlx.vcf import fromvcf, unpackinfo
        >>> from petl import look
        >>> t1 = fromvcf('../fixture/sample.vcf', samples=False)
        >>> look(t1)
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        | 'CHROM' | 'POS'   | 'ID'        | 'REF' | 'ALT'     | 'QUAL' | 'FILTER' | 'INFO'                                                                                  |
        +=========+=========+=============+=======+===========+========+==========+=========================================================================================+
        | '19'    |     111 | None        | 'A'   | [C]       |    9.6 | []       | {}                                                                                      |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        | '19'    |     112 | None        | 'A'   | [G]       |     10 | []       | {}                                                                                      |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        | '20'    |   14370 | 'rs6054257' | 'G'   | [A]       |     29 | []       | OrderedDict([('NS', 3), ('DP', 14), ('AF', [0.5]), ('DB', True), ('H2', True)])         |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        | '20'    |   17330 | None        | 'T'   | [A]       |      3 | ['q10']  | OrderedDict([('NS', 3), ('DP', 11), ('AF', [0.017])])                                   |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        | '20'    | 1110696 | 'rs6040355' | 'A'   | [G, T]    |     67 | []       | OrderedDict([('NS', 2), ('DP', 10), ('AF', [0.333, 0.667]), ('AA', 'T'), ('DB', True)]) |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        | '20'    | 1230237 | None        | 'T'   | [None]    |     47 | []       | OrderedDict([('NS', 3), ('DP', 13), ('AA', 'T')])                                       |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        | '20'    | 1234567 | 'microsat1' | 'G'   | [GA, GAC] |     50 | []       | OrderedDict([('NS', 3), ('DP', 9), ('AA', 'G'), ('AN', 6), ('AC', [3, 1])])             |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        | '20'    | 1235237 | None        | 'T'   | [None]    | None   | []       | {}                                                                                      |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        | 'X'     |      10 | 'rsTest'    | 'AC'  | [A, ATG]  |     10 | []       | {}                                                                                      |
        +---------+---------+-------------+-------+-----------+--------+----------+-----------------------------------------------------------------------------------------+
        
        >>> t2 = unpackinfo(t1)
        >>> look(t2)
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
        | 'CHROM' | 'POS'   | 'ID'        | 'REF' | 'ALT'     | 'QUAL' | 'FILTER' | 'NS' | 'AN' | 'AC'   | 'DP' | 'AF'           | 'AA' | 'DB' | 'H2' |
        +=========+=========+=============+=======+===========+========+==========+======+======+========+======+================+======+======+======+
        | '19'    |     111 | None        | 'A'   | [C]       |    9.6 | []       | None | None | None   | None | None           | None | None | None |
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
        | '19'    |     112 | None        | 'A'   | [G]       |     10 | []       | None | None | None   | None | None           | None | None | None |
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
        | '20'    |   14370 | 'rs6054257' | 'G'   | [A]       |     29 | []       |    3 | None | None   |   14 | [0.5]          | None | True | True |
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
        | '20'    |   17330 | None        | 'T'   | [A]       |      3 | ['q10']  |    3 | None | None   |   11 | [0.017]        | None | None | None |
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
        | '20'    | 1110696 | 'rs6040355' | 'A'   | [G, T]    |     67 | []       |    2 | None | None   |   10 | [0.333, 0.667] | 'T'  | True | None |
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
        | '20'    | 1230237 | None        | 'T'   | [None]    |     47 | []       |    3 | None | None   |   13 | None           | 'T'  | None | None |
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
        | '20'    | 1234567 | 'microsat1' | 'G'   | [GA, GAC] |     50 | []       |    3 |    6 | [3, 1] |    9 | None           | 'G'  | None | None |
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
        | '20'    | 1235237 | None        | 'T'   | [None]    | None   | []       | None | None | None   | None | None           | None | None | None |
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
        | 'X'     |      10 | 'rsTest'    | 'AC'  | [A, ATG]  |     10 | []       | None | None | None   | None | None           | None | None | None |
        +---------+---------+-------------+-------+-----------+--------+----------+------+------+--------+------+----------------+------+------+------+
    
    .. versionadded:: 0.5
    
    """
    if not keys:
        if hasattr(tbl, 'filename'):
            try:
                import vcf as pyvcf
            except ImportError as e:
                raise UnsatisfiedDependency(e, dep_message)
            reader = pyvcf.Reader(filename=tbl.filename)
            # all INFO
            keys = reader.infos.keys()
    result = unpackdict(tbl, 'INFO', keys=keys)
    if 'prefix' in kwargs:
        result = rename(result, {k: kwargs['prefix'] + k for k in keys})
    if hasattr(tbl, 'filename'):
        return VCFWrapper(result, tbl.filename)
    else:
        return result
    
    
def meltsamples(tbl, *samples):
    """
    Melt the samples columns. E.g.::
    
        >>> from petlx.vcf import fromvcf, unpackinfo, meltsamples
        >>> from petl import look, cutout
        >>> t1 = fromvcf('../fixture/sample.vcf')
        >>> t2 = meltsamples(t1)
        >>> t3 = cutout(t2, 'INFO')
        >>> look(t3)
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | 'CHROM' | 'POS' | 'ID'        | 'REF' | 'ALT' | 'QUAL' | 'FILTER' | 'SAMPLE'  | 'CALL'                                                               |
        +=========+=======+=============+=======+=======+========+==========+===========+======================================================================+
        | '19'    |   111 | None        | 'A'   | [C]   |    9.6 | []       | 'NA00001' | Call(sample=NA00001, CallData(GT=0|0, HQ=[10, 10]))                  |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | '19'    |   111 | None        | 'A'   | [C]   |    9.6 | []       | 'NA00002' | Call(sample=NA00002, CallData(GT=0|0, HQ=[10, 10]))                  |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | '19'    |   111 | None        | 'A'   | [C]   |    9.6 | []       | 'NA00003' | Call(sample=NA00003, CallData(GT=0/1, HQ=[3, 3]))                    |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | '19'    |   112 | None        | 'A'   | [G]   |     10 | []       | 'NA00001' | Call(sample=NA00001, CallData(GT=0|0, HQ=[10, 10]))                  |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | '19'    |   112 | None        | 'A'   | [G]   |     10 | []       | 'NA00002' | Call(sample=NA00002, CallData(GT=0|0, HQ=[10, 10]))                  |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | '19'    |   112 | None        | 'A'   | [G]   |     10 | []       | 'NA00003' | Call(sample=NA00003, CallData(GT=0/1, HQ=[3, 3]))                    |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | '20'    | 14370 | 'rs6054257' | 'G'   | [A]   |     29 | []       | 'NA00001' | Call(sample=NA00001, CallData(GT=0|0, GQ=48, DP=1, HQ=[51, 51]))     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | '20'    | 14370 | 'rs6054257' | 'G'   | [A]   |     29 | []       | 'NA00002' | Call(sample=NA00002, CallData(GT=1|0, GQ=48, DP=8, HQ=[51, 51]))     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | '20'    | 14370 | 'rs6054257' | 'G'   | [A]   |     29 | []       | 'NA00003' | Call(sample=NA00003, CallData(GT=1/1, GQ=43, DP=5, HQ=[None, None])) |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        | '20'    | 17330 | None        | 'T'   | [A]   |      3 | ['q10']  | 'NA00001' | Call(sample=NA00001, CallData(GT=0|0, GQ=49, DP=3, HQ=[58, 50]))     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+----------------------------------------------------------------------+
        
    .. versionadded:: 0.5
    
    """
    result = melt(tbl, key=fixed_fields, variables=samples, variablefield='SAMPLE', valuefield='CALL')
    if hasattr(tbl, 'filename'):
        return VCFWrapper(result, tbl.filename)
    else:
        return result
    
          
def unpackcall(tbl, *keys, **kwargs):
    """
    Unpack the call column. E.g.::
    
        >>> from petlx.vcf import fromvcf, unpackinfo, meltsamples, unpackcall
        >>> from petl import look, cutout
        >>> t1 = fromvcf('../fixture/sample.vcf')
        >>> t2 = meltsamples(t1)
        >>> t3 = unpackcall(t2)
        >>> t4 = cutout(t3, 'INFO')
        >>> look(t4)
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | 'CHROM' | 'POS' | 'ID'        | 'REF' | 'ALT' | 'QUAL' | 'FILTER' | 'SAMPLE'  | 'GT'  | 'GQ' | 'DP' | 'HQ'         |
        +=========+=======+=============+=======+=======+========+==========+===========+=======+======+======+==============+
        | '19'    |   111 | None        | 'A'   | [C]   |    9.6 | []       | 'NA00001' | '0|0' | None | None | [10, 10]     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | '19'    |   111 | None        | 'A'   | [C]   |    9.6 | []       | 'NA00002' | '0|0' | None | None | [10, 10]     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | '19'    |   111 | None        | 'A'   | [C]   |    9.6 | []       | 'NA00003' | '0/1' | None | None | [3, 3]       |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | '19'    |   112 | None        | 'A'   | [G]   |     10 | []       | 'NA00001' | '0|0' | None | None | [10, 10]     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | '19'    |   112 | None        | 'A'   | [G]   |     10 | []       | 'NA00002' | '0|0' | None | None | [10, 10]     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | '19'    |   112 | None        | 'A'   | [G]   |     10 | []       | 'NA00003' | '0/1' | None | None | [3, 3]       |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | '20'    | 14370 | 'rs6054257' | 'G'   | [A]   |     29 | []       | 'NA00001' | '0|0' |   48 |    1 | [51, 51]     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | '20'    | 14370 | 'rs6054257' | 'G'   | [A]   |     29 | []       | 'NA00002' | '1|0' |   48 |    8 | [51, 51]     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | '20'    | 14370 | 'rs6054257' | 'G'   | [A]   |     29 | []       | 'NA00003' | '1/1' |   43 |    5 | [None, None] |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        | '20'    | 17330 | None        | 'T'   | [A]   |      3 | ['q10']  | 'NA00001' | '0|0' |   49 |    3 | [58, 50]     |
        +---------+-------+-------------+-------+-------+--------+----------+-----------+-------+------+------+--------------+
        
    .. versionadded:: 0.5
    
    """
    if not keys:
        if hasattr(tbl, 'filename'):
            try:
                import vcf as pyvcf
            except ImportError as e:
                raise UnsatisfiedDependency(e, dep_message)
            reader = pyvcf.Reader(filename=tbl.filename)
            # all FORMAT
            keys = reader.formats.keys()
        else:
            tbl = convert(tbl, 'CALL', lambda v: v.data._asdict()) # enable sampling of keys from data
    result = unpackdict(tbl, 'CALL', keys=keys)
    if 'prefix' in kwargs:
        result = rename(result, {k: kwargs['prefix'] + k for k in keys})
    if hasattr(tbl, 'filename'):
        return VCFWrapper(result, tbl.filename)
    else:
        return result
    
      
import sys    
from .integration import integrate
integrate(sys.modules[__name__])
