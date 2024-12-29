import sys
from newyear_tootgen.post import post_toot


if __name__ == "__main__":
    post_toot(sys.argv[1], False)
