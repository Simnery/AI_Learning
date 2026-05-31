---
name: explore-data
description: 快速浏览和分析数据集（CSV/JSON/Parquet/HuggingFace）。当用户要求看数据、分析数据集时调用。
allowed-tools: Read Write Bash
---

# 数据集快速浏览分析

## 分析项

1. **基本信息**: 行数、列数、dtypes、缺失值统计
2. **数值列**: describe（均值、方差、分位数）、分布建议
3. **分类列**: unique 值数量、最高频类别、分布
4. **文本列**: 平均/最大长度
5. **数据质量**: 重复行、异常值检测
6. **可视化建议**: 适合该数据结构的图表类型

## 规则

- 数据量 >100MB 时先采样分析
- 始终生成简明的中文分析报告
