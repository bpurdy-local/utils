import math


class Integer:
    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0

    @staticmethod
    def is_odd(n: int) -> bool:
        return n % 2 != 0

    @staticmethod
    def clamp(n: int, *, min_val: int, max_val: int) -> int:
        return max(min_val, min(n, max_val))

    @staticmethod
    def to_roman(n: int) -> str:
        if not 0 < n < 4000:
            raise ValueError("Integer must be between 1 and 3999")
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
        roman_num = ""
        i = 0
        num = n
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num

    @staticmethod
    def to_words(n: int) -> str:
        if n == 0:
            return "zero"
        ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        tens = [
            "",
            "",
            "twenty",
            "thirty",
            "forty",
            "fifty",
            "sixty",
            "seventy",
            "eighty",
            "ninety",
        ]
        teens = [
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
        ]

        def convert_hundreds(num: int) -> str:
            if num == 0:
                return ""
            result = ""
            if num >= 100:
                result += ones[num // 100] + " hundred"
                num %= 100
                if num > 0:
                    result += " "
            if num >= 20:
                result += tens[num // 10]
                if num % 10 > 0:
                    result += "-" + ones[num % 10]
            elif num >= 10:
                result += teens[num - 10]
            elif num > 0:
                result += ones[num]
            return result

        num = abs(n)
        if num == 0:
            return "zero"
        result = ""
        if n < 0:
            result = "negative "
        if num >= 1000000000:
            result += convert_hundreds(num // 1000000000) + " billion"
            num %= 1000000000
            if num > 0:
                result += " "
        if num >= 1000000:
            result += convert_hundreds(num // 1000000) + " million"
            num %= 1000000
            if num > 0:
                result += " "
        if num >= 1000:
            result += convert_hundreds(num // 1000) + " thousand"
            num %= 1000
            if num > 0:
                result += " "
        if num > 0:
            result += convert_hundreds(num)
        return result.strip()

    @staticmethod
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        return all(n % i != 0 for i in range(3, int(n**0.5) + 1, 2))

    @staticmethod
    def factorial(n: int) -> int:
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    @staticmethod
    def gcd(n: int, *, other: int) -> int:
        return math.gcd(n, other)

    @staticmethod
    def lcm(n: int, *, other: int) -> int:
        return abs(n * other) // math.gcd(n, other)

    @staticmethod
    def is_power_of(n: int, *, base: int) -> bool:
        if n <= 0 or base <= 1:
            return False
        num = abs(n)
        while num > 1:
            if num % base != 0:
                return False
            num //= base
        return True

    @staticmethod
    def digits(n: int) -> list[int]:
        return [int(d) for d in str(abs(n))]

    @staticmethod
    def reverse(n: int) -> int:
        sign = -1 if n < 0 else 1
        return sign * int(str(abs(n))[::-1])

    @staticmethod
    def bytes_to_human(n: int) -> str:
        size = float(abs(n))
        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} EB"

    @staticmethod
    def percentage(n: int, *, total: int, decimals: int = 1) -> float:
        if total == 0:
            return 0.0
        return round((abs(n) / total) * 100, decimals)
