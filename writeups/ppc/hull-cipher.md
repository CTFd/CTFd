<!-- nctf-meta category="ppc" difficulty="easy" points="150" author="dagbanjaphet" stub="0" -->

# hull-cipher

The flag characters sit on the convex hull of the point cloud; walking the hull
in order spells the flag.

## Technique

`points.txt` starts with a count, then one `x y ch` line per point. The flag
characters were placed on a large circle (so each is a vertex of the convex
hull), ordered so that a counter-clockwise walk starting at the bottom-most
vertex reproduces the flag. Every other point lies strictly inside the circle
and is therefore never a hull vertex.

## Steps

1. Parse the points and remember the character attached to each coordinate.
2. Compute the convex hull (Andrew's monotone chain, `O(n log n)`).
3. Orient the hull counter-clockwise (flip it if the signed area is negative).
4. Rotate the vertex list so it begins at the vertex with the smallest
   `(y, x)`.
5. Concatenate the characters of the hull vertices in that order.

Run `python3 solution/solve.py` (pure standard library).

## Complexity

`O(n log n)` for the sort/hull over a few hundred points — instant.

## Flag

`NCTF{…}`
