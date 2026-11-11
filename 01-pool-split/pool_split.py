def split_pool(pool_cents: int, weights: list[int]) -> list[int]:
    """按权重分配奖池，保证所有人的金额之和等于奖池总额。"""
    # 金额和权重必须是整数，避免出现半分钱或浮点误差。
    if not isinstance(pool_cents, int) or any(
        not isinstance(weight, int) for weight in weights
    ):
        raise TypeError("pool_cents and weights must be integers")
    # 确保奖池和权重为非负数。
    if pool_cents < 0 or any(weight < 0 for weight in weights):
        raise ValueError("pool and weights must be non-negative")
    # total 权重之和，作为比例计算的分母。
    total = sum(weights)
    if total == 0:
        raise ValueError("weights must have a positive total")

    shares = []
    remainders = []
    for weight in weights:
        # divmod 同时返回整数商 share 和余数 remainder。
        share, remainder = divmod(pool_cents * weight, total)
        shares.append(share)
        remainders.append(remainder)

    # 计算剩余需要分的。
    cents_left = pool_cents - sum(shares)

    # order 保存用户的索引。
    order = list(range(len(weights)))
    # 根据位置对应的余数从大到小排序；相同余数保留原输入顺序。
    order.sort(key=lambda index: remainders[index], reverse=True)

    # 按余数优先级给前 cents_left 个用户各补 1 分。
    for i in order[:cents_left]:
        shares[i] += 1

    # 返回列表与输入 weights 的位置一一对应。
    return shares
