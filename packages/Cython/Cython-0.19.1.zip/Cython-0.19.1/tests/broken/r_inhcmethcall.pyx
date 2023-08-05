cdef class Parrot:

  cdef void describe(self):
    print "This parrot is resting."


cdef class Norwegian(Parrot):

  cdef void describe(self):
    Parrot.describe(self)
    print "Lovely plumage!"


cdef Parrot p1, p2
p1 = Parrot()
p2 = Norwegian()
p1.describe()
p2.describe()
