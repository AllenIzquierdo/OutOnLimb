
points = []
def generateHalfPoint(lower,upper):
    return (lower+upper)/2

def generateSearchPoints(lower,upper, hitmarker = -1, rangemarker = -1, bounds = [0,1], includeExtremes = False):
    pointsearch = []
    if hitmarker == -1:
        hitmarker = generateHalfPoint(lower,upper)
        pointsearch.append(hitmarker)

    lowerRange = hitmarker - lower;
    upperRange = upper - hitmarker;

    # Apply range maker bounds
    if rangemarker>0:
        if lowerRange > rangemarker:
            lower = hitmarker - rangemarker
        if upperRange > rangemarker:
            upper = hitmarker + rangemarker
            print('assigning upper range')
    # Apply extreme bounds
    if lower < bounds[0]:
        lower = bounds[0]
    if upper > bounds[1]:
        upper = bounds[1]
        print('assinning upper bounds')
    
    # order by size
    lowerRange = hitmarker - lower;
    upperRange = upper - hitmarker;
    if upperRange > lowerRange:
        pointsearch.append(generateHalfPoint(hitmarker,upper))
        pointsearch.append(generateHalfPoint(lower,hitmarker))
    else:
        pointsearch.append(generateHalfPoint(lower,hitmarker))
        pointsearch.append(generateHalfPoint(hitmarker,upper))
        
    # Include boudnaires
    if includeExtremes:
        pointsearch.append(lower)
        pointsearch.append(upper)

    return pointsearch
