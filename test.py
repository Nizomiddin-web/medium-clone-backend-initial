def left_right_difference(nums: list) -> list:
    """ kodni davom etkazing """
    result = []
    for i in nums:
        a = sum(nums[:nums.index(i)+1])
        b = sum(nums[nums.index(i)+1:])
        if a > b:
            result.append(-1)
        elif a < b:
            result.append(1)
            print(a)
            print(b)
        elif a == b:
            result.append(0)

    return result


print(left_right_difference([1, 100, 1]))
