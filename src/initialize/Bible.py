from src.Bible.usfm import read_Bible_USFM

def import_ASV():
    result = read_Bible_USFM("content/Bible/ASV", skip=["00-FRTeng-asv.usfm", "01-INTeng-asv.usfm"])
    print(result)

if __name__ == "__main__":
    import_ASV()
