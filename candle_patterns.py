import pandas as pd

# ---- All 33 Candle Patterns ----

# 1. Bullish Engulfing
def bullish_engulfing(df):
    prev = df.shift(1)
    return (prev['Close'] < prev['Open']) & (df['Close'] > df['Open']) & (df['Open'] < prev['Close']) & (df['Close'] > prev['Open'])

# 2. Bearish Engulfing
def bearish_engulfing(df):
    prev = df.shift(1)
    return (prev['Close'] > prev['Open']) & (df['Close'] < df['Open']) & (df['Open'] > prev['Close']) & (df['Close'] < prev['Open'])

# 3. Hammer
def hammer(df):
    body = abs(df['Close'] - df['Open'])
    return ((df['Open'] - df['Low'] > 2 * body) | (df['Close'] - df['Low'] > 2 * body)) & (df['High'] - df[['Open', 'Close']].max(axis=1) < body)

# 4. Shooting Star
def shooting_star(df):
    body = abs(df['Close'] - df['Open'])
    return ((df['High'] - df['Open'] > 2 * body) | (df['High'] - df['Close'] > 2 * body)) & (df[['Open', 'Close']].min(axis=1) - df['Low'] < body)

# 5. Doji
def doji(df):
    body = abs(df['Close'] - df['Open'])
    return body <= ((df['High'] - df['Low']) * 0.1)

# 6. Morning Star
def morning_star(df):
    prev = df.shift(1)
    prev2 = df.shift(2)
    return (prev2['Close'] < prev2['Open']) & (abs(prev['Close'] - prev['Open']) < (prev['High'] - prev['Low']) * 0.3) & (df['Close'] > df['Open']) & (df['Close'] > ((prev2['Open'] + prev2['Close']) / 2))

# 7. Evening Star
def evening_star(df):
    prev = df.shift(1)
    prev2 = df.shift(2)
    return (prev2['Close'] > prev2['Open']) & (abs(prev['Close'] - prev['Open']) < (prev['High'] - prev['Low']) * 0.3) & (df['Close'] < df['Open']) & (df['Close'] < ((prev2['Open'] + prev2['Close']) / 2))

# 8. Piercing Pattern
def piercing(df):
    prev = df.shift(1)
    mid = (prev['Open'] + prev['Close']) / 2
    return (prev['Close'] < prev['Open']) & (df['Open'] < prev['Close']) & (df['Close'] > mid) & (df['Close'] < prev['Open'])

# 9. Dark Cloud Cover
def dark_cloud(df):
    prev = df.shift(1)
    mid = (prev['Open'] + prev['Close']) / 2
    return (prev['Close'] > prev['Open']) & (df['Open'] > prev['Close']) & (df['Close'] < mid) & (df['Close'] > prev['Open'])

# 10. Three White Soldiers
def three_white_soldiers(df):
    prev1 = df.shift(1)
    prev2 = df.shift(2)
    return (df['Close'] > df['Open']) & (prev1['Close'] > prev1['Open']) & (prev2['Close'] > prev2['Open']) & (df['Close'] > prev1['Close']) & (prev1['Close'] > prev2['Close'])

# 11. Three Black Crows
def three_black_crows(df):
    prev1 = df.shift(1)
    prev2 = df.shift(2)
    return (df['Close'] < df['Open']) & (prev1['Close'] < prev1['Open']) & (prev2['Close'] < prev2['Open']) & (df['Close'] < prev1['Close']) & (prev1['Close'] < prev2['Close'])

# 12. Tweezer Top
def tweezer_top(df):
    prev = df.shift(1)
    return (prev['High'] == df['High']) & (prev['Close'] > prev['Open']) & (df['Close'] < df['Open'])

# 13. Tweezer Bottom
def tweezer_bottom(df):
    prev = df.shift(1)
    return (prev['Low'] == df['Low']) & (prev['Close'] < prev['Open']) & (df['Close'] > df['Open'])

# 14. Bullish Harami
def bullish_harami(df):
    prev = df.shift(1)
    return (prev['Close'] < prev['Open']) & (df['Open'] > prev['Close']) & (df['Close'] < prev['Open'])

# 15. Bearish Harami
def bearish_harami(df):
    prev = df.shift(1)
    return (prev['Close'] > prev['Open']) & (df['Open'] < prev['Close']) & (df['Close'] > prev['Open'])

# 16. Bullish Kicker
def bullish_kicker(df):
    prev = df.shift(1)
    return (prev['Close'] < prev['Open']) & (df['Open'] > prev['Open']) & (df['Close'] > df['Open'])

# 17. Bearish Kicker
def bearish_kicker(df):
    prev = df.shift(1)
    return (prev['Close'] > prev['Open']) & (df['Open'] < prev['Open']) & (df['Close'] < df['Open'])

# 18. Rising Three Methods
def rising_three_methods(df):
    prev1 = df.shift(1)
    prev2 = df.shift(2)
    prev3 = df.shift(3)
    return (prev3['Close'] > prev3['Open']) & (prev2['Close'] < prev2['Open']) & (prev1['Close'] < prev1['Open']) & (df['Close'] > df['Open']) & (df['Close'] > prev3['Close'])

# 19. Falling Three Methods
def falling_three_methods(df):
    prev1 = df.shift(1)
    prev2 = df.shift(2)
    prev3 = df.shift(3)
    return (prev3['Close'] < prev3['Open']) & (prev2['Close'] > prev2['Open']) & (prev1['Close'] > prev1['Open']) & (df['Close'] < df['Open']) & (df['Close'] < prev3['Close'])

# 20. Marubozu
def marubozu(df):
    body = abs(df['Close'] - df['Open'])
    shadow = (df['High'] - df['Close']) + (df['Open'] - df['Low'])
    return shadow <= (body * 0.1)

# 21. Spinning Top
def spinning_top(df):
    body = abs(df['Close'] - df['Open'])
    range_ = df['High'] - df['Low']
    return (body / range_) < 0.3

# 22. Long Legged Doji
def long_legged_doji(df):
    body = abs(df['Close'] - df['Open'])
    range_ = df['High'] - df['Low']
    return (body < range_ * 0.1) & ((df['High'] - df[['Open','Close']].max(axis=1)) > range_ * 0.4) & ((df[['Open','Close']].min(axis=1) - df['Low']) > range_ * 0.4)

# 23. Dragonfly Doji
def dragonfly_doji(df):
    body = abs(df['Close'] - df['Open'])
    return (body < (df['High'] - df['Low']) * 0.1) & ((df['High'] - df[['Open','Close']].max(axis=1)) < body)

# 24. Gravestone Doji
def gravestone_doji(df):
    body = abs(df['Close'] - df['Open'])
    return (body < (df['High'] - df['Low']) * 0.1) & ((df[['Open','Close']].min(axis=1) - df['Low']) < body)

# 25. Inverted Hammer
def inverted_hammer(df):
    body = abs(df['Close'] - df['Open'])
    upper = df['High'] - df[['Open','Close']].max(axis=1)
    lower = df[['Open','Close']].min(axis=1) - df['Low']
    return (upper > 2 * body) & (lower < body)

# 26. Hanging Man
def hanging_man(df):
    body = abs(df['Close'] - df['Open'])
    lower = df[['Open','Close']].min(axis=1) - df['Low']
    upper = df['High'] - df[['Open','Close']].max(axis=1)
    return (lower > 2 * body) & (upper < body)

# 27. Belt Hold
def belt_hold(df):
    body = abs(df['Close'] - df['Open'])
    return (body / (df['High'] - df['Low']) > 0.7) & ((df['Open'] == df['Low']) | (df['Open'] == df['High']))

# 28. Mat Hold
def mat_hold(df):
    prev1 = df.shift(1)
    prev2 = df.shift(2)
    prev3 = df.shift(3)
    prev4 = df.shift(4)
    return (prev4['Close'] > prev4['Open']) & (prev3['Close'] < prev3['Open']) & (prev2['Close'] < prev2['Open']) & (prev1['Close'] < prev1['Open']) & (df['Close'] > df['Open']) & (df['Close'] > prev4['Close'])

# 29. Kicking Pattern
def kicking(df):
    prev = df.shift(1)
    gap = abs(prev['Close'] - df['Open']) > ((prev['High'] - prev['Low']) * 0.5)
    return ((prev['Close'] < prev['Open']) & (df['Close'] > df['Open']) & gap) | ((prev['Close'] > prev['Open']) & (df['Close'] < df['Open']) & gap)

# 30. Stick Sandwich
def stick_sandwich(df):
    prev = df.shift(1)
    prev2 = df.shift(2)
    return (prev2['Close'] < prev2['Open']) & (prev['Close'] > prev['Open']) & (df['Close'] < df['Open']) & (df['Close'] == prev2['Close'])

# 31. Rising Window
def rising_window(df):
    prev = df.shift(1)
    return df['Low'] > prev['High']

# 32. Falling Window
def falling_window(df):
    prev = df.shift(1)
    return df['High'] < prev['Low']

# 33. On Neck Line
def on_neck_line(df):
    prev = df.shift(1)
    return (prev['Close'] < prev['Open']) & (df['Open'] < prev['Low']) & (df['Close'] == prev['Low'])
