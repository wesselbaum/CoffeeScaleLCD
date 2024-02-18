def getTargetWeightFromGroundsWeight(groundsWeight, relationshipGrounds = 1, relationshipWater = 16):
    return int(groundsWeight / relationshipGrounds * relationshipWater)
