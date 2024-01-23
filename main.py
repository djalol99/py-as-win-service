import sys
wservice = __import__("wservice")

class ScaleService(wservice.BaseService): ...

if __name__ == "__main__":
    ScaleService.run(sys.argv)

