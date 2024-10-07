def left_right_difference(nums: list) -> list:
    """ kodni davom etkazing """
    result = []
    for i in nums:
        a = sum(nums[:nums.index(i) + 1])
        b = sum(nums[nums.index(i) + 1:])
        if a > b:
            result.append(-1)
        elif a < b:
            result.append(1)
            print(a)
            print(b)
        elif a == b:
            result.append(0)

    return result


def rim_number_change_to_number(rim_number):
    """
    Vazifa tavsifi:
    Rim raqamlari etti xil belgilar bilan ifodalanadi: I, V, X, L, C, D va M
    Belgi qiymati

    I 1

    V 5

    X 10

    L 50

    C 100

    D 500

    M 1000
    """
    change_dict = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000
    }
    result = []
    for i in rim_number:
        result.append(change_dict[i])
    result2 = []
    i = 0
    j = 1
    for a in result:
        if len(result) == 1:
            return a
        if j >= len(result):
            return sum(result2)
        if result[i] >= result[j]:
            result2.append(result[i])
            i += 1
            j += 1
            if j >= len(result):
                result2.append(result[-1])
                return sum(result2)
        else:
            result2.append(result[j] - result[i])
            i += 2
            j += 2


# print(rim_number_change_to_number('I'))


def remove_element(nums: list[int], val: int) -> int:
    k = 0
    for i in range(len(nums)):
        if nums[i] != val:
            nums[k] = nums[i]
            k += 1
    return len(nums)


def str_str(haystack: str, needle: str) -> int:
    a = haystack.find(needle)
    print(a)


print(str_str("hellolloollooll", "kskks"))
