try:
    from pythonize import strings
    context='RAPYDSCRIPT'
    strings()
    #from __python__ import dict_literals, overload_getitem
except ModuleNotFoundError:
    context='PYTHON'

print('context', context)

class DICT():
    def __init__( self, *args, **kwargs ):
        # print('\n args kwargs',args, kwargs)
        # self._germ='DICT'
        if len( args ) == 1:
            if type( args[ 0 ] ) == type( {} ):  # convert an object
                # self._germ='{}'
                obj = args[ 0 ]
                keys = Object.keys( obj )
                values = Object.values( obj )
                for i in range( len( keys ) ):
                    k = keys[ i ]
                    v = values[ i ]
                    self[ k ] = v
                    # print(k,v,'\t',end='')
            else:
                if type( args[ 0 ] ) == type( dict() ):  # convert a dict
                    d = args[ 0 ]
                    # self._germ='dict()'
                    for k, v in zip( d.keys(), d.values() ):
                        if not k.startswith( '_' ):
                            self[ k ] = v

        for kwarg in kwargs:
            self[ kwarg ] = kwargs[ kwarg ]

    def keys( self ):
        return [ key for key in Object.keys( self ) if not key.startswith( '_' ) ]

    def values( self ):
        vs = [ ]
        for k, v in zip( Object.keys( self ), Object.values( self ) ):
            if not k.startswith( '_' ):
                vs.append( v )
        return vs

    def items( self ):
        l = [ ]
        for k in self.keys():
            l.append( (k, self[ k ]) )
        return l

    def __next__( self ):
        return 'next'

    def __repr__( self ):
        pairs = zip( self.keys(), self.values() )  # make kv pairs
        elems = [ str( k ) + ':' + str( v ) for k, v in pairs if not k.startswith( '_' ) ]
        elems = str( elems )
        elems = elems.replace( '[', '{' ).replace( ']', '}' )
        while '"' in elems:
            elems = elems.replace( '"', '' )
        return  elems



if __name__=='__main__':
    #tests
    D=DICT()
    print(D)
    D = DICT( a=1, b=2 )
    D[ 'c' ] = 3
    D.d = 4
    print( "D.keys()\t",    D.keys()   )
    print( "D.values()\t",  D.values() )
    print( "D.items()\t",   D.items()   )
    print( "D",             D          )
    print("D['a']==D.a", D['a']==D.a)



    #timing tests show that DICT is no worse than rapydscript's dict but both are worse than javascript Object
kinds=DICT('     {}' = {},
            'DICT()' = DICT(),
            'dict()' = dict())
def runTests():
    for name in kinds:
        console.time(name)
        for i in range(1000000):
            kinds[name][ 'c' ] = 3
        console.timeEnd(name)
        D=kinds[name]
        try:
            print('D',D,    '\t\tD.keys()', D.keys(),  '\t\tD.values()', D.values(),     '\t\tD.items()', D.items())
        except TypeError:
            print('Type error: keys, values, items, are not functions')
        print()


print('\nwithout dict_literals')
runTests()
from __python__ import dict_literals, overload_getitem
print('\n\nWITH dict_literals')
runTests()

"""
#see: context
context RAPYDSCRIPT

#good printing

{}
D.keys()	 ["a", "b", "c", "d"]
D.values()	 [1, 2, 3, 4]
D.items()	 [["a", 1], ["b", 2], ["c", 3], ["d", 4]]
D {a:1, b:2, c:3, d:4}
D['a']==D.a True

without dict_literals
     {}: 5.068ms
Type error: keys, values, items, are not functions
# nothing to show

DICT(): 26.921ms
D {c:3} 		D.keys() ["c"] 		D.values() [3] 		D.items() [["c", 3]]
#good printing

dict(): 34.902ms
D {} 		D.keys() [object Map Iterator] 		D.values() [object Map Iterator] 		D.items() [object Map Iterator]
#opaque


WITH dict_literals
#dict literals slow {} and somewhat DICT

     {}: 24.405ms
Type error: keys, values, items, are not functions

DICT(): 36.860ms
D {c:3} 		D.keys() ["c"] 		D.values() [3] 		D.items() [["c", 3]]

dict(): 34.072ms
D {} 		D.keys() [object Map Iterator] 		D.values() [object Map Iterator] 		D.items() [object Map Iterator]




"""







