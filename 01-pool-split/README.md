# Pool Split

按权重分配整数金额，使用最大余数法保证分配总额始终等于奖池金额。

```powershell
cd 01-pool-split
py -m unittest -v test_pool_split
```

测试包含一分钱分给三人、相同余数、零权重、无效输入和超大整数等场景。

