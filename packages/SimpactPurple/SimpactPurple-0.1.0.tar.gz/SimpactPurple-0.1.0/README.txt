===========
Simpact Purple
===========

*Simpact Purple* is a module for agent-based simulations of HIV and other sexually transmitted diseases and is part of a suite of HIV modeling tools known as *Simpact*. It is a useful tool for public health officials and epidemiologists which implements a parallelized algorithm based on queue theory. Typical usage::

    #!/usr/bin/env python

    import Simpact

    if __name__ == '__main__':
        s = Simpact.Simpact()
	s.INITIAL_POPULATION = 1000
	s.run() 



