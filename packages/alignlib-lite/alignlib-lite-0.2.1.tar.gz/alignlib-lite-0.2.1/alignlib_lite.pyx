# distutils: language = c++
# distutils: sources = alignlib_src/*.cpp

from cython.operator cimport dereference as deref
from libcpp.string cimport string

# import boost shared_ptr definition
cdef extern from 'boost/shared_ptr.hpp' namespace 'boost':

    cdef cppclass shared_ptr[T]:
        shared_ptr()
        shared_ptr(T*)
        shared_ptr(shared_ptr[T]&)
        T* get()
        long use_count()
        #void reset(shared_ptr[T]&)

# import types
cdef extern from "alignlib.h" namespace "alignlib":
    ctypedef int Position
    ctypedef double Score

    ctypedef enum CombinationMode: 
        RR
        RC
        CR
        CC

######################################################################
# wrapping alignlib functions:
#
# cdef cppclass Alignment:
#      ....
#
# ctypedef shared_ptr[Alignment] HAlignment
# HAlignment py_makeAlignmentVector()
#
# cdef class py_Alignment:
#      cdef HAlignment thisptr


######################################################################
# Alignment
cdef extern from "Alignment.h" namespace "alignlib":
    cdef cppclass Alignment:
        Alignment() except +

        void setScore( Score score ) except +
        Score getScore() except +
        Position getRowFrom() except +
        Position getRowTo() except +
        Position getColFrom() except +
        Position getColTo() except +
        Position mapRowToCol( Position row ) except +
        void addDiagonal( Position row_from, Position row_to, Position col_offset ) except +
        int getNumAligned() except +


cdef extern from "HelpersAlignment.h" namespace "alignlib":

    ctypedef shared_ptr[Alignment] HAlignment 

    HAlignment makeAlignmentVector()
    HAlignment makeAlignmentBlocks()

    Position getAlignmentIdentity( HAlignment, HAlignment, CombinationMode mode ) except +
    Position getAlignmentOverlap( HAlignment, HAlignment, CombinationMode mode ) except +


######################################################################
cdef extern from "AlignmentFormat.h" namespace "alignlib":
    cdef cppclass AlignmentFormat:
        AlignmentFormat() except +
        AlignmentFormat(HAlignment) except +
        AlignmentFormat(str) except +
        AlignmentFormat(AlignmentFormat) except +
        void fill(HAlignment)
        void copy(HAlignment)
        Position mRowFrom
        Position mRowTo        
        Position mColFrom
        Position mColTo

    cdef cppclass AlignmentFormatBlocks(AlignmentFormat):
        AlignmentFormatBlocks() except +
        AlignmentFormatBlocks(HAlignment) except +

    cdef cppclass AlignmentFormatBlat(AlignmentFormat):
        AlignmentFormatBlat() except +
        AlignmentFormatBlat(HAlignment) except +


######################################################################
## conversion utilities
cdef extern from "alignlib_cython.h" namespace 'alignlib':

    cdef string Alignment2String( HAlignment & )
    cdef string AlignmentFormat2String( AlignmentFormat * )

#######################################################################
#######################################################################
#######################################################################
## Python interface classes
#######################################################################
#######################################################################
## Alignment
#######################################################################
cdef class py_Alignment:
    cdef HAlignment thisptr
        
    def __cinit__(self, container = 'vector' ):
        if container == "vector":
            self.thisptr = makeAlignmentVector()
        elif container == "blocks":
            self.thisptr = makeAlignmentBlocks()

    def getScore(self):
        return deref(self.thisptr.get()).getScore()

    def setScore(self, score):
        deref(self.thisptr.get()).setScore( score )

    def getRowFrom( self ): return deref(self.thisptr.get()).getRowFrom()
    def getRowTo( self ): return deref(self.thisptr.get()).getRowTo()
    def getColFrom( self ): return deref(self.thisptr.get()).getColFrom()
    def getColTo( self ): return deref(self.thisptr.get()).getColTo()
    def mapRowToCol( self, row ): return deref(self.thisptr.get()).mapRowToCol( row )
    def getNumAligned( self ): return deref(self.thisptr.get()).getNumAligned()

    def addDiagonal( self, row_from, row_to, col_offset ):
        deref(self.thisptr.get()).addDiagonal( row_from, row_to, col_offset )

    def __str__(self):
        return Alignment2String( self.thisptr )

    cdef HAlignment exportPointer( self ):
        return self.thisptr

##############################################################################
##############################################################################
##############################################################################
## HelpersAlignment
##############################################################################
def py_makeAlignmentVector():
    '''return an alignment vector.'''
    return py_Alignment( container = "vector" )

def py_makeAlignmentBlocks():
    '''return an alignment vector.'''
    return py_Alignment( container = "blocks" )

def py_getAlignmentIdentity( py_Alignment a, py_Alignment b, CombinationMode mode ):
    return getAlignmentIdentity( a.thisptr, b.thisptr, mode )

def py_getAlignmentOverlap( py_Alignment a, py_Alignment b, CombinationMode mode ):
    return getAlignmentOverlap( a.thisptr, b.thisptr, mode )

##############################################################################
##############################################################################
##############################################################################
cdef class py_AlignmentFormat:
    cdef AlignmentFormat *thisptr
    def __cinit__(self, other = None ):
        self.thisptr = new AlignmentFormat()
    def __dealloc__(self):
        del self.thisptr
    def fill(self, py_Alignment alignment):
        self.thisptr.fill( alignment.thisptr )
    def __str__(self):
        return AlignmentFormat2String( self.thisptr )

cdef class py_AlignmentFormatBlocks( py_AlignmentFormat ):
    def __cinit__(self, other = None):
        cdef py_Alignment o
        if other == None:
            self.thisptr = new AlignmentFormatBlocks()
        elif type( other ) == py_Alignment:
            o = <py_Alignment?>other
            self.thisptr = new AlignmentFormatBlocks( o.exportPointer() )

cdef class py_AlignmentFormatBlat( py_AlignmentFormat ):
    def __cinit__(self, other = None):
        cdef py_Alignment o
        if other == None:
            self.thisptr = new AlignmentFormatBlat()
        elif type( other ) == py_Alignment:
            o = <py_Alignment?>other
            self.thisptr = new AlignmentFormatBlat( o.exportPointer() )

###########################################################################
###########################################################################
###########################################################################
## export enums
cdef public enum:
    py_RR = RR    
    py_RC = RC
    py_CR = CR
    py_CC = CC
