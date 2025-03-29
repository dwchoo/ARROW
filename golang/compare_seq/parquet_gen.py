#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas
dataframe = pandas.DataFrame({
        "A": ["a", "b", "c", "d"],
        "B": [2, 3, 4, 1],
        "C": [True, True, True, True]
    })

dataframe.to_parquet("1.parquet")
