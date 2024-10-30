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


# print(str_str("hellolloollooll", "kskks"))

# def convert_to_title(columnNumber: int) -> str:
#     a = {
#         1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H',
#         9: 'I', 10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O',
#         16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T', 21: 'U', 22: 'V',
#         23: 'W', 24: 'X', 25: 'Y', 26: 'Z'
#     }
#     if columnNumber < 27:
#         return a[columnNumber]
#     qoldiq = columnNumber % 26
#     print(qoldiq)
#     butun = int(columnNumber / 26)
#     print(butun)
#     if qoldiq == 0:
#         print("saa")
#         return f"{a[butun-1]}{a[26]}"
#     return f"{a[butun]}{a[qoldiq]}"
#

# print(convert_to_title(52))

def is_isomorphic(s: str, t: str) -> bool:
    dicts = {}
    s_list = list(s)
    t_list = list(t)
    for i in range(len(s_list)):
        if not dicts:
            dicts[s_list[i]] = t_list[i]
        else:
            if not s_list[i] in dicts:
                dicts[s_list[i]] = t_list[i]
            else:
                print(dicts[s_list[i]] != t_list[i])
                if dicts[s_list[i]] != t_list[i]:
                    return False
    return True


# print(is_isomorphic("foo", "bar"))

def is_happy(n: int) -> bool:
    seen=set()
    while n!=0 and n not in seen:
        seen.add(n)
        n=sum(int(i)**2 for i in str(n))
        print(n)
    return n==1

# is_happy(7)

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:  # Agar almashinish bo'lmasa, chiqish
            break
    return arr

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        # Katta elementlarni o‘ngga surish
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key  # Elementni joylashtirish
    return arr

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]  # O‘rta elementni pivot sifatida tanlash
    left = [x for x in arr if x < pivot]  # Pivotdan kichik elementlar
    middle = [x for x in arr if x == pivot]  # Pivotga teng elementlar
    right = [x for x in arr if x > pivot]  # Pivotdan katta elementlar
    return quick_sort(left) + middle + quick_sort(right)



print(quick_sort([1,24,34,33,23,19,3,90,34]))

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid  # Target topildi
        elif arr[mid] < target:
            left = mid + 1  # O'ng qismga o‘tish
        else:
            right = mid - 1  # Chap qismga o‘tish
    return -1  # Target topilmadi

def linear_search(arr, target):
     for index,val in enumerate(arr):
         if val==target:
             return index
     return -1



print(linear_search([1,223,2,32,32,54,67,342,21],32))

def factorial(n):
    if n==0:
        return 1
    else:
        return n*factorial(n-1)

# print(factorial(8))


def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


# print(fibonacci(7))


print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))
print(quick_sort([64, 34, 25, 12, 22, 11, 90]))

print(binary_search([1, 2, 3, 4, 5, 6, 7, 8, 9],5))










