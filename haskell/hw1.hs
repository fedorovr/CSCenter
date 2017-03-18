module HW1 where

-- represent swap as   f (g h)
swap' :: (a, b) -> (b, a)
swap' = uncurry (flip (,))


fib :: Integer -> Integer 
fib n = helper (1, 0) n
    where 
        helper p n | n == 0 = snd p
        helper p n | otherwise = helper (fst p + snd p, fst p) (n - 1) 


fibRec :: Integer -> Integer
fibRec n = helper n
    where 
        helper n | n == 0 = 0
        helper n | n == 1 = 1
        helper n | otherwise = helper (n - 1) + helper (n - 2)


doubleFact :: Integer -> Integer
doubleFact n = if n > 1 then n * doubleFact(n - 2) else 1


seqA :: Integer -> Integer
seqA n = helper (3, 2, 1) n
    where
        helper (_, _, c) n | n == 0 = c
        helper (a, b, c) n | otherwise = helper (a + b - (2 * c), a, b) (n - 1)


fibNeg :: Integer -> Integer 
fibNeg n = if n < 0 then ((-1)^(-n - 1) * (helper (1, 0) (-n))) else (helper (1, 0) n)
    where 
        helper p n | n == 0 = snd p
        helper (f_cur, f_prev) n | otherwise = helper (f_cur + f_prev, f_cur) (n - 1)


sum'n'count :: Integer -> (Integer, Integer)
sum'n'count x = (forDigit (\x -> x `mod` 10) (abs x) 0, max 1 (forDigit (\_ -> 1) (abs x) 0)) 
    where
        forDigit _ n acc | n == 0 = acc
        forDigit f n acc | otherwise = forDigit f (n `div` 10) (acc + f n)


integration :: (Double -> Double) -> Double -> Double -> Double
integration f a b = (sign' a b) * (helper 0.0 (min a b) (abs (a - b) / 1000000) (max a b))
    where
        helper acc cur step right | cur >= right = acc
        helper acc cur step right | otherwise = helper (acc + (f cur) * step) (cur + step) step right
        sign' a b = if a <= b then 1.0 else -1.0 
