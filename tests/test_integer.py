import pytest

from utils import Integer


class TestIntegerProperties:
    def test_is_even(self):
        assert Integer.is_even(4) is True
        assert Integer.is_even(5) is False
        assert Integer.is_even(0) is True
        assert Integer.is_even(-2) is True

    def test_is_odd(self):
        assert Integer.is_odd(5) is True
        assert Integer.is_odd(4) is False
        assert Integer.is_odd(1) is True
        assert Integer.is_odd(-3) is True

    def test_is_prime(self):
        assert Integer.is_prime(2) is True
        assert Integer.is_prime(3) is True
        assert Integer.is_prime(7) is True
        assert Integer.is_prime(8) is False
        assert Integer.is_prime(1) is False
        assert Integer.is_prime(0) is False
        assert Integer.is_prime(-5) is False


class TestIntegerClamp:
    def test_clamp_above_max(self):
        assert Integer.clamp(15, min_val=0, max_val=10) == 10

    def test_clamp_below_min(self):
        assert Integer.clamp(-5, min_val=0, max_val=10) == 0

    def test_clamp_within_range(self):
        assert Integer.clamp(5, min_val=0, max_val=10) == 5

    def test_clamp_at_boundaries(self):
        assert Integer.clamp(0, min_val=0, max_val=10) == 0
        assert Integer.clamp(10, min_val=0, max_val=10) == 10

    def test_clamp_negative_range(self):
        assert Integer.clamp(-15, min_val=-10, max_val=-5) == -10
        assert Integer.clamp(-3, min_val=-10, max_val=-5) == -5


class TestIntegerConversions:
    def test_to_roman_basic(self):
        assert Integer.to_roman(1) == "I"
        assert Integer.to_roman(4) == "IV"
        assert Integer.to_roman(5) == "V"
        assert Integer.to_roman(9) == "IX"
        assert Integer.to_roman(10) == "X"

    def test_to_roman_larger_numbers(self):
        assert Integer.to_roman(50) == "L"
        assert Integer.to_roman(100) == "C"
        assert Integer.to_roman(500) == "D"
        assert Integer.to_roman(1000) == "M"
        assert Integer.to_roman(1994) == "MCMXCIV"

    def test_to_roman_invalid_range(self):
        with pytest.raises(ValueError):
            Integer.to_roman(0)
        with pytest.raises(ValueError):
            Integer.to_roman(4000)

    def test_to_words_basic(self):
        assert Integer.to_words(0) == "zero"
        assert Integer.to_words(1) == "one"
        assert Integer.to_words(10) == "ten"
        assert Integer.to_words(20) == "twenty"

    def test_to_words_hundreds(self):
        result = Integer.to_words(123)
        assert "one hundred" in result
        assert "twenty-three" in result

    def test_to_words_thousands(self):
        result = Integer.to_words(1234)
        assert "one thousand" in result


class TestIntegerMath:
    def test_factorial_basic(self):
        assert Integer.factorial(0) == 1
        assert Integer.factorial(1) == 1
        assert Integer.factorial(5) == 120

    def test_factorial_negative(self):
        with pytest.raises(ValueError):
            Integer.factorial(-1)

    def test_lcm_basic(self):
        assert Integer.lcm(12, other=18) == 36
        assert Integer.lcm(5, other=7) == 35

    def test_is_power_of(self):
        assert Integer.is_power_of(8, base=2) is True
        assert Integer.is_power_of(9, base=3) is True
        assert Integer.is_power_of(16, base=2) is True
        assert Integer.is_power_of(10, base=2) is False
        assert Integer.is_power_of(1, base=2) is True

    def test_is_power_of_invalid(self):
        assert Integer.is_power_of(0, base=2) is False
        assert Integer.is_power_of(5, base=1) is False


class TestIntegerDigits:
    def test_digits_basic(self):
        assert Integer.digits(123) == [1, 2, 3]
        assert Integer.digits(0) == [0]
        assert Integer.digits(100) == [1, 0, 0]

    def test_digits_negative(self):
        assert Integer.digits(-123) == [1, 2, 3]

    def test_reverse_basic(self):
        assert Integer.reverse(123) == 321
        assert Integer.reverse(100) == 1
        assert Integer.reverse(0) == 0

    def test_reverse_negative(self):
        assert Integer.reverse(-123) == -321
