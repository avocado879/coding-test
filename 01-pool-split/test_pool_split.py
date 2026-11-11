import unittest
from itertools import product

from pool_split import split_pool


class PoolSplitTests(unittest.TestCase):
    # 原实现会把 1 分分成 [0, 0, 0]，导致少发 1 分。
    def test_one_cent_regression_case(self):
        self.assertEqual(split_pool(1, [1, 1, 1]), [1, 0, 0])

    # 检查余数相同时按顺序分配，以及零权重用户不拿钱。
    def test_largest_remainder_ties_and_zero_weights(self):
        self.assertEqual(split_pool(2, [1, 1, 1]), [1, 1, 0])
        self.assertEqual(split_pool(10, [1, 0, 2]), [3, 0, 7])

    # 多种小输入和超大金额都必须把奖池完整分完。
    def test_conserves_pool_for_many_inputs_and_large_values(self):
        # 测试 1 到 4 人、权重为 0 到 3 的组合，以及 0 到 12 分的奖池。
        for length in range(1, 5):
            for weights in product(range(4), repeat=length):
                if sum(weights) == 0:
                    continue
                for pool in range(13):
                    shares = split_pool(pool, list(weights))
                    self.assertEqual(len(shares), len(weights))
                    self.assertEqual(sum(shares), pool)

        # 超大整数也应准确分配，不受浮点精度影响。
        pool = 10**40 + 1
        self.assertEqual(
            split_pool(pool, [1, 1, 1]),
            [pool // 3 + 1, pool // 3 + 1, pool // 3],
        )

    # 无效权重或非整数输入应明确报错。
    def test_rejects_invalid_inputs(self):
        for pool, weights in [(1, []), (1, [0, 0]), (-1, [1]), (1, [1, -1])]:
            with self.subTest(pool=pool, weights=weights):
                with self.assertRaises(ValueError):
                    split_pool(pool, weights)
        with self.assertRaises(TypeError):
            split_pool(1.5, [1])
        with self.assertRaises(TypeError):
            split_pool(1, [1, 0.5])


if __name__ == "__main__":
    unittest.main()
