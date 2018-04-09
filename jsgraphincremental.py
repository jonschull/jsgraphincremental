# GlowScript 2.7 VPython
from vpython import *

scene = canvas()
V = vector


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

    def __str__( self ):
        pairs = zip( self.keys(), self.values() )  # make kv pairs
        elems = [ str( k ) + ':' + str( v ) for k, v in pairs if not k.startswith( '_' ) ]
        elems = str( elems )
        elems = elems.replace( '[', '{' ).replace( ']', '}' )
        while '"' in elems:
            elems = elems.replace( '"', '' )
        return 'DO:' + elems


DICT = dict


def _hooke( n1, n2, k, r ):
    # print('n1, n2, k, r', n1, n2, k, r)
    "Calculates Hooke spring forces and updates node data."
    # Get relevant positional data

    delta = [ x2 - x1 for x1, x2 in zip( n1[ 'velocity' ], n2[ 'velocity' ] ) ]
    # print('delta', delta)

    distance = sqrt( sum( [ d ** 2 for d in delta ] ) )

    # If the deltas are too small, use random values to keep things moving
    if distance < 0.1:
        delta = [ 0.1 + random() * 0.1 for i in range( 3 ) ]
        distance = sqrt( sum( [ d ** 2 for d in delta ] ) )

    # Truncate distance so as to not have crazy springiness
    distance = min( distance, r )

    # Calculate Hooke force and update nodes
    force = (distance ** 2 - k ** 2) / (distance * k)
    n1[ 'force' ] = [ f + force * d for f, d in zip( n1[ 'force' ], delta ) ]
    n2[ 'force' ] = [ f - force * d for f, d in zip( n2[ 'force' ], delta ) ]


def _constrain( value, min_value, max_value ):
    "--Constrains a value to the inputted range--."
    return max( min_value, min( value, max_value ) )


def vFromLoc( loc ):
    if len( loc ) < 3:
        loc.append( 0 )
    x, y, z = loc
    return vector( x, y, z )


def nodesFromEdges( edges ):
    nodes = [ ]
    for edge in edges:
        s, t = edge
        for node in (s, t):
            if node not in nodes:
                nodes.append( node )
    return nodes


def generate( edges ):
    iterations = 1000
    force_strength = 5.0
    dampening = 0.01
    max_velocity = 2.0
    max_distance = 50
    is_3d = False
    # Outputs a json-serializable Python object. To visualize, pass the output to
    # `jgraph.draw(...)`.

    ##    print('params', data, iterations, force_strength, dampening,
    ##             max_velocity, max_distance, is_3d)
    global spheres, labels, curves
    # edges = [{'source': s, 'target': t} for s, t in data]
    # --------put run in line

    # Get a list of node ids from the edge data
    nodeIDs = [ ]
    for edge in edges:
        for nodeID in edge:
            if nodeID not in nodeIDs:
                nodeIDs.append( nodeID )

    # Convert to a data-storing object and initialize some values
    d = 3 if is_3d else 2

    nodes = DICT()
    for nodeID in nodeIDs:
        nodes[ nodeID ] = DICT( {'velocity': [ 0.0 ] * d, 'force': [ 0.0 ] * d}, ID=nodeID )

    def combinations( iter='ABCD', len=2 ):  # ONLY works for len=2!  #NOW INLINE
        combos = [ ]
        for i in iter:
            for j in iter:
                if i != j:
                    if (i, j) not in combos:
                        if (j, i) not in combos:
                            combos.append( (i, j) )
        return combos

    # print('nodes', str(nodes))
    for i in range( iterations ):
        # global spheres, labels, curves
        # begin coulomb
        for node1, node2 in combinations( nodes.values(), 2 ):
            r = max_distance
            k = force_strength
            delta = [ x2 - x1 for x1, x2 in zip( node1[ 'velocity' ], node2[ 'velocity' ] ) ]
            ddd = sum( [ d ** 2 for d in delta ] )
            distance = sqrt( ddd )

            # If the deltas are too small, use random values to keep things moving
            if distance < 0.1:
                delta = [ 0.1 + ((0.2 - 0.1) * random()) for i in range( 3 ) ]
                ddd = [ d ** 2 for d in delta ]
                distance = sqrt( sum( ddd ) )
                # print('distance, delta', distance, delta)

            # If the distance isn't huge (ie. Coulomb is negligible), calculate
            if distance < r:
                force = (k / distance) ** 2
                node1[ 'force' ] = [ f - force * d for f, d in zip( node1[ 'force' ], delta ) ]
                node2[ 'force' ] = [ f + force * d for f, d in zip( node2[ 'force' ], delta ) ]

        for edge in edges:
            # print('edge',edge)  #HOOKE IS NULLING Force
            s, t = edge
            _hooke( nodes[ s ], nodes[ t ], force_strength, max_distance )

        # Move by resultant force
        # print(i,' preMv', str(nodes))
        for node in nodes.values():
            # Constrain the force to the bounds specified by input parameter
            force = [ _constrain( dampening * f, -max_velocity, max_velocity )
                      for f in node[ 'force' ] ]
            # Update velocities and reset force
            node[ 'velocity' ] = [ v + dv
                                   for v, dv in zip( node[ 'velocity' ], force ) ]

            ID = node[ 'ID' ]
            spheres[ ID ].pos = vFromLoc( node[ 'velocity' ] )
            labels[ ID ].pos = spheres[ ID ].pos
            node[ 'force' ] = [ 0 ] * d
            rate( 800 )

        for edge in edges:
            s, t = edge
            c = curves( s, t )
            c.clear()
            c.append( [ spheres[ s ].pos, spheres[ t ].pos ] )
    ##
    # print(i,'postMv', str(nodes))

    # Clean and return
    for node in nodes.values():
        del node[ 'force' ]
        node[ 'location' ] = node[ 'velocity' ]
        del node[ 'velocity' ]
        # Even if it's 2D, let's specify three dimensions
        if not is_3d:
            node[ 'location' ].append( 0 )

    # -------put run in line

    return {'edges': edges, 'nodes': nodes}


data = edges = [ (1, 2), (2, 3), (3, 1), (2, 4), (2, 5) ]
spheres = DICT()
labels = DICT()

twoferDict = DICT()


def twofer( x='', y='', z='' ):
    """convenient look up for two dimensional thingsj like edges or XYpoints"""
    global twoferDict

    if x == '':  # twofer()
        if not twoferDict: return {}

        keys = [ eval( k ) for k in twoferDict.keys() ]
        values = twoferDict.values()
        return list( zip( keys, values ) )

    if x == 'keys':  # twofer('keys')
        return [ eval( k ) for k in twoferDict.keys() ]

    if x == 'values':  # twofer('values')
        return list( twoferDict.values() )

    if x == 'items':  # twofer('items)
        keys = [ eval( k ) for k in twoferDict.keys() ]
        return list( zip( keys, twoferDict.values() ) )

    if z != '':  # twofer(x,y,z) sets twofer(x,y) to z; return z
        twoferDict[ str( (x, y) ) ] = z
        return z
    else:
        if str( (x, y) ) in twoferDict:  # twofer(x,y) returns z
            return twoferDict[ str( (x, y) ) ]
        else:
            raise KeyError( str( (x, y) ) )  # unless twofer(x,y) doesn't exist


curves = twofer

# create nodes
nodes = nodesFromEdges( data )
for node in nodes:
    s = sphere()
    spheres[ node ] = s
    l = label( text=str( node ) )
    l.pos = s.pos
    labels[ node ] = l

for edge in edges:
    s, t = edge
    spos = spheres[ s ].pos
    tpos = spheres[ t ].pos
    curves( s, t, curve( pos=[ spos, tpos ] ) )

generate( data )  # this is where the work gets done
